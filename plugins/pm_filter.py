import asyncio
import re
import math
import time
import base64
from datetime import datetime, timedelta
import pytz
from urllib.parse import quote
from Script import script
import aiohttp
import ast
from info import SLOW_MODE_DELAY, ADMINS, AUTH_GROUPS, FORCESUB_CHANNEL, WAIT_TIME, BIN_CHANNEL, URL, ACCESS_KEY, SUPPORT_GROUP
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
from database.users_chats_db import db
from database.config_db import mdb
from pyrogram.errors import MessageNotModified
from utils import get_size, is_subscribed, search_gagala, temp, replace_blacklist, fetch_quote_content
from plugins.shortner import shortlink as link_shortner
from plugins.paid_filter import paid_filter
from plugins.free_filter import free_filter
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import find_filter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

@Client.on_message(filters.private & filters.text & filters.incoming)
async def filters_private_handlers(client, message):

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    if message.text.startswith("/"):
        return
    
    url_pattern = re.compile(r'https?://\S+')
    if message.from_user.id not in ADMINS:
        if re.search(url_pattern, message.text):
            await message.delete()
            return

    now = datetime.now()
    tody = int(now.timestamp())
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    user_timestamps = user.get("timestamps")
    files_counts = user.get("files_count")
    premium_status = await db.is_premium_status(user_id)
    last_reset = user.get("last_reset")
    referral = await db.fetch_value(user_id, "referral")
    duration = user.get("premium_expiry")

    kolkata = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.now(kolkata)
    next_day = current_datetime + timedelta(days=1)
    next_day_midnight = datetime(next_day.year, next_day.month, next_day.day, tzinfo=kolkata)
    time_difference = (next_day_midnight - current_datetime).total_seconds() / 3600
    time_difference = round(time_difference)
    today = datetime.now(kolkata).strftime("%Y-%m-%d")

    maintenance_mode = await mdb.get_configuration_value("maintenance_mode")
    one_file_one_link = await mdb.get_configuration_value("one_link")
    private_filter = await mdb.get_configuration_value("private_filter")
    no_ads = await mdb.get_configuration_value("no_ads")
    forcesub = await mdb.get_configuration_value("forcesub")

    # update top messages
    await mdb.update_top_messages(message.from_user.id, message.text)   

    if FORCESUB_CHANNEL and forcesub and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(FORCESUB_CHANNEL), creates_join_request=True)
        except Exception as e:
            logger.error(e)
        btn = [
            [InlineKeyboardButton("Join now", url=invite_link.invite_link)],
            [InlineKeyboardButton("Try again", callback_data="checkjoin")]
        ]
        await message.reply_text(
            f"<b>🐾 Due to overload only channel subscriber can use this bot.</b>\nPlease join my channel to use this bot",
            reply_markup=InlineKeyboardMarkup(btn),
        )
        return
    
    if referral is not None and referral >= 50:
        await db.update_value(user_id, "referral", referral - 50)
        await db.add_user_as_premium(user_id, 28, tody)
        await message.reply_text(f"**Congratulations! {message.from_user.mention},\nYou Have Received 1 Month Premium Subscription For Inviting 5 Users.**", disable_web_page_preview=True)
        return
        
    if last_reset != today:
        await db.reset_all_files_count()
        await mdb.delete_all_messages()
    
    if maintenance_mode is True:
        await message.reply_text(f"<b>Sorry For The Inconvenience, We Are Under Maintenance. Please Try Again Later</b>", disable_web_page_preview=True)
        return
    
    if private_filter is False:
        return
 
    msg = await message.reply_text(f"<b>Searching For Your Request...</b>", reply_to_message_id=message.id)
    
    files, _, _ = await get_search_results(message.text.lower(), offset=0, filter=True)
    if not files:
        google = "https://google.com/search?q="
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Check Your Spelling", url=f"{google}{quote(message.text.lower())}%20movie")],
            [InlineKeyboardButton("🗓 Check Release Date", url=f"{google}{quote(message.text.lower())}%20release%20date")]
        ])
        await msg.edit(
            text="<b>I couldn't find a movie in my database. Please check the spelling or the release date and try again.</b>",
            reply_markup=reply_markup,
        )
        return      
    
    filter = None
    try:
        if premium_status is True:
            if await db.check_expired_users(user_id):
                await msg.edit(f"<b>Your Premium Subscription Has Been Expired. Please <a href=https://t.me/{temp.U_NAME}?start=upgrade>Renew</a> Your Subscription To Continue Using Premium.</b>", disable_web_page_preview=True)
                return
            if files_counts >= 100:
                await msg.edit(f"<b>Your Account Has Been Locked Due To Spamming, And It'll Be Unlocked After {time_difference} Hours.</b>")
                return
            if duration == 28 and files_counts >= 30:
                await msg.edit(f"<b>You Can Only Get 30 Files a Day, Please Wait For {time_difference} Hours To Request Again</b>")
                return
                
            text, markup = await paid_filter(client, message)
            filter = await msg.edit(text=text, reply_markup=markup, disable_web_page_preview=True)

        elif no_ads is True:
            text, markup = await paid_filter(client, message)
            filter = await msg.edit(text=text, reply_markup=markup, disable_web_page_preview=True)

        else:
            if user_timestamps:
                current_time = int(time.time())
                time_diff = current_time - user_timestamps
                if time_diff < SLOW_MODE_DELAY:
                    remaining_time = SLOW_MODE_DELAY - time_diff
                    while remaining_time > 0:
                        await msg.edit(f"<b>Please Wait For {remaining_time} Seconds Before Sending Another Request.</b>")
                        await asyncio.sleep(1)
                        remaining_time = max(0, SLOW_MODE_DELAY - int(time.time()) + user_timestamps)
                    await message.delete()
                    await msg.delete()
                    return

            if not one_file_one_link and files_counts >= 15:
                await msg.edit(
                    f"<b>You Have Reached Your Daily Limit. Please Try After {time_difference} Hours, or  <a href=https://t.me/{temp.U_NAME}?start=upgrade>Upgrade</a> To Premium For Unlimited Request.</b>",
                    disable_web_page_preview=True)
                return
        
            try:
                if one_file_one_link and (files_counts is not None and files_counts >= 1):
                    text , button = await free_filter(client, message)
                else:
                    text, button = await auto_filter(client, message)
        
                filter = await msg.edit(text=text, reply_markup=button, disable_web_page_preview=True)  
            except:
                logger.error("Error in auto filter")

    except Exception as e:
        await msg.edit(f"<b>Opps! Something Went Wrong.</b>")

    finally:
        await asyncio.sleep(WAIT_TIME)
        if filter:
            await filter.delete()

@Client.on_message(filters.group & filters.text & filters.incoming)
async def public_group_filter(client, message):

    if message.text.startswith("/") or not await mdb.get_configuration_value("group_filter"):
        return
    
    files_counts = await db.fetch_value(message.from_user.id, "files_count")
    one_time_ads = await mdb.get_configuration_value("one_link_one_file_group")
    no_ads = await mdb.get_configuration_value("no_ads")
    premium = await db.is_premium_status(message.from_user.id)
    await mdb.update_top_messages(message.from_user.id, message.text)
    
    filter = None
    try:
        if premium:
            text, button = await paid_filter(client, message)

        elif no_ads is True:
            text, button = await paid_filter(client, message)

        elif message.chat.id in AUTH_GROUPS and one_time_ads and files_counts >= 1:
            text, button = await free_filter(client, message)   

        else:
            text, button = await auto_filter(client, message)

        filter = await message.reply(text=text, reply_markup=button, disable_web_page_preview=True)

    except Exception as e:
        logger.error(e)

    finally:
        if WAIT_TIME is not None:
            await asyncio.sleep(WAIT_TIME)
            if filter:
                await filter.delete()
                

@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("Not For You", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You are clicking on an old button which is expired.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for Movie in database...')
    files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        text, button = await auto_filter(bot, query, k)
        await query.message.edit(text, reply_markup=button, disable_web_page_preview=True)
    else:
        k = await query.message.edit('This Movie Not Found In My DataBase')
        await asyncio.sleep(10)
        await k.delete()


async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("I couldn't find any movie in that name.")
        await asyncio.sleep(8)
        await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply("I couldn't find anything related to that. Check your spelling")
        await asyncio.sleep(8)
        await k.delete()
        return
    SPELL_CHECK[msg.id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"spolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    await msg.reply(f"<b>Did you mean any one of these?</b>",
                    reply_markup=InlineKeyboardMarkup(btn))
    
    
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    # get user name in query.answer
    m = int(req)
    k = await bot.get_users(m)
    name = k.first_name if not k.last_name else k.first_name + " " + k.last_name
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(f"**{name}**\nonly can access this query", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    # Construct a text message with hyperlinks
    search_results_text = []
    for file in files:
        shortlink = await link_shortner(f"https://telegram.me/{temp.U_NAME}?start=file_{file.file_id}")
        file_link = f"🎬 [{get_size(file.file_size)} | {await replace_blacklist(file.file_name, script.BLACKLIST)}]({shortlink})"
        search_results_text.append(file_link)

    search_results_text = "\n\n".join(search_results_text)

    btn = []
    btn.append([InlineKeyboardButton("🔴 𝐇𝐎𝐖 𝐓𝐎 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃 🔴", url="https://t.me/QuickAnnounce/5")])
    
    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
         await query.edit_message_text(
            text=f"<b>{search_results_text}</b>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()
    
    
async def auto_filter(_, msg, spoll=False):
    if not spoll:
        message = msg
        if message.text.startswith("/"):
            return
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if await mdb.get_configuration_value("spoll_check"):
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message
        search, files, offset, total_results = spoll
    search_results_text = []
    for file in files:
        shortlink = await link_shortner(f"https://telegram.me/{temp.U_NAME}?start=file_{file.file_id}")
        file_link = f"🎬 [{get_size(file.file_size)} | {await replace_blacklist(file.file_name, script.BLACKLIST)}]({shortlink})"
        search_results_text.append(file_link)

    search_results_text = "\n\n".join(search_results_text)

    btn = []   
    btn.append([
            InlineKeyboardButton("🪙 Upgrade", callback_data="upgrade_call"),
            InlineKeyboardButton("🔗 Refer", callback_data="refer_call")
        ])
    
    # Ads Placement in auto filter
    ads, ads_name, _ = await mdb.get_advirtisment()
    if ads is not None and ads_name is not None:
        btn.append([InlineKeyboardButton(text=f"📢 {ads_name}", url=f"https://t.me/{temp.U_NAME}?start=ads")])

    btn.append([InlineKeyboardButton("🔴 𝐇𝐎𝐖 𝐓𝐎 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃 🔴", url="https://t.me/QuickAnnounce/5")])
    
    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    cap = f"Here is what i found for your query {search}"
    # add timestamp to database for floodwait
    await db.update_value(message.from_user.id, "timestamps", int(time.time()))
    return f"<b>{cap}\n\n{search_results_text}</b>", InlineKeyboardMarkup(btn)

   
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        _, btn, alerts, _ = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)

    if query.data.startswith("checksub"):
        if FORCESUB_CHANNEL and not await is_subscribed(client, query):
            await query.answer("Please Join My Channel Then Click Try Again 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        md_id=await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f"<code>{await replace_blacklist(f_caption, script.BLACKLIST)}</code>",
        )
        del_msg = await client.send_message(
            text=f"<b>File will be deleted in 10 mins. Save or forward immediately.<b>",
            chat_id=query.from_user.id,
            reply_to_message_id=md_id.id
            )
        await asyncio.sleep(WAIT_TIME or 600)
        await md_id.delete()
        await del_msg.edit("__⊘ This message was deleted__")

    elif query.data == "pages":
        qoute = await fetch_quote_content()
        await query.answer(f"**{qoute}**", show_alert=True)
    elif query.data == "home":
        buttons = [[
                    InlineKeyboardButton('📎 Refer', callback_data="refer"),
                    InlineKeyboardButton('🔥 Top Search', callback_data="topsearch")
                    ],[
                    InlineKeyboardButton('🎟️ Upgrade ', callback_data="remads"),
                    InlineKeyboardButton('🗣️ Request', callback_data="request")
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit(
        text=script.START_TXT.format(query.from_user.mention, temp.B_NAME),
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        )
        if not await db.is_user_exist(query.from_user.id):
            await db.add_user(
                query.from_user.id,
                query.from_user.first_name
                )
        
    elif query.data == "close_data":
        await query.message.delete()
    elif query.data == "request":
        buttons = [[
                    InlineKeyboardButton('📽️ Request Group', url=f"https://t.me/+yea6oolZNRpjZjBl"),
                    InlineKeyboardButton('◀️ Back', callback_data="home")
                ]]
        await query.message.edit(
        text=script.REQM,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        )                
    elif query.data == "remads":
        buttons = [[
                    InlineKeyboardButton('💫 Pay', callback_data="confirm"),
                    InlineKeyboardButton('◀️ Back', callback_data="home")
                ]]
        tnc= f"<a href=https://t.me/{temp.U_NAME}?start=terms>T&C apply</a>"
        await query.message.edit(
        text=script.REMADS_TEXT.format(tnc),
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        )
       
    elif query.data == "confirm":
        buttons = [[
                    InlineKeyboardButton('📣 Help', url="https://t.me/caredeskbot"),
                    InlineKeyboardButton('◀️ Back', callback_data="remads"),
                ]]
        await query.message.edit(
        text=script.CNFRM_TEXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        )

    elif query.data == "place_ads":
        button = [[
            InlineKeyboardButton('📣 Support', url="https://t.me/caredeskbot"),
            InlineKeyboardButton('◀️ Back', callback_data="home")
        ]]
        await query.message.edit(
            text=script.ADS_TEXT,
            reply_markup=InlineKeyboardMarkup(button),
            disable_web_page_preview=True
        )

    elif query.data == "checkjoin":
        forcesub = await mdb.get_configuration_value("forcesub")
        if FORCESUB_CHANNEL and forcesub and not await is_subscribed(client, query):
            await query.answer("Please join in my channel dude!", show_alert=True)
        else:
            await query.answer("Thanks for joining, Now you can continue searching", show_alert=True)
            await query.message.delete()

    elif query.data == "refer":
        user_id = query.from_user.id
        referral_points = await db.fetch_value(user_id, "referral")
        refferal_link = f"https://t.me/{temp.U_NAME}?start=ReferID-{user_id}"
        buttons = [[
                    InlineKeyboardButton('🎐 Invite', url=f"https://telegram.me/share/url?url={refferal_link}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83"),
                    InlineKeyboardButton(f"🟢 {referral_points}", callback_data="refer_point"),
                    InlineKeyboardButton('◀️ Back', callback_data="home")
                ]]
        await query.message.edit(
            text=f"<b>Here is your refferal link:\n\n{refferal_link}\n\nShare this link with your friends, Each time they join, Both of you will get 10 refferal points and after 50 points you will get 1 month premium subscription.</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    elif query.data == "refer_point":
        user_id = query.from_user.id
        referral_points = await db.fetch_value(user_id, "referral")
        await query.answer(f"You have {referral_points} refferal points.", show_alert=True
        )
    
    elif query.data == "upgrade_call":
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=upgrade")
        return
    
    elif query.data == "refer_call":
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=refer")
        return
    
    elif query.data == "terms":
        buttons = [[
                    InlineKeyboardButton("✅ Accept Terms", callback_data="home"),
                ]]
        await query.message.edit(
            text=script.TERMS,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    # Function to delete unwanted files
    elif query.data == "delback":
        keyboard_buttons = [
            ["PreDVD", "PreDVDRip"],
            ["HDTS", "HDTC"],
            ["HDCam", "Sample"],
            ["CamRip", "Print"]
        ]

        btn = [
            [InlineKeyboardButton(button, callback_data=button.lower().replace("-", "")) for button in row]
            for row in keyboard_buttons
        ]
        btn.append(
            [InlineKeyboardButton("⛔️ Close", callback_data="close_data")]
            )

        await query.message.edit(
            text="<b>Select The Type Of Files You Want To Delete..?</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        
    elif query.data in ["predvd", "camrip", "predvdrip", "hdcam", "hdcams", "print", "hdts", "sample", "hdtc"]:
        buttons = [[
            InlineKeyboardButton("10", callback_data=f"dlt#10_{query.data}")
            ],[
            InlineKeyboardButton("100", callback_data=f"dlt#100_{query.data}")
            ],[
            InlineKeyboardButton("1000", callback_data=f"dlt#1000_{query.data}")
            ],[
            InlineKeyboardButton('⛔️ Close', callback_data="close_data"),
            InlineKeyboardButton('◀️ Back', callback_data="delback")
        ]]
        await query.message.edit(
            text=f"<b>How Many {query.data.upper()} Files You Want To Delete?</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
    
    elif query.data.startswith("dlt#"):
        limit, file_type = query.data.split("#")[1].split("_")
        buttons = [[
            InlineKeyboardButton('Hell No', callback_data=f"confirm_no")
            ],[           
            InlineKeyboardButton('Yes, Delete', callback_data=f"confirm_yes#{limit}_{file_type}")
            ],[
            InlineKeyboardButton('⛔️ Close', callback_data="close_data")
        ]]
        await query.message.edit(
            text=f"<b>Are You Sure To Delete {limit} {file_type.upper()} Files?</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
    elif query.data.startswith("confirm_yes#"):
        limits, file_type = query.data.split("#")[1].split("_")
        limit = int(limits)
        await delete_files(query, limit, file_type)

    elif query.data == "confirm_no":
        await query.message.edit(text=f"<b>Deletion canceled.</b>", reply_markup=None)

    # Function for getting the top search results
    elif query.data == "topsearch":
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=topsearch")
        return
     
    elif query.data == "topsearches":

        def is_valid_string(string):
            return bool(re.match('^[a-zA-Z0-9 ]*$', string))

        await query.answer(f"<b>Fetching Top Searches, Be Patience It'll Take Some Time</b>", show_alert=True)
        top_searches = await mdb.get_top_messages(20)

        unique_messages = set()
        truncated_messages = []

        for msg in top_searches:
            if msg.lower() not in unique_messages and is_valid_string(msg):
                unique_messages.add(msg.lower())

                files, _, _ = await get_search_results(msg.lower())
                if files:
                    if len(msg) > 20:
                        truncated_messages.append(msg[:20 - 3])
                    else:
                        truncated_messages.append(msg)

        # Display two buttons in a row
        keyboard = []
        for i in range(0, len(truncated_messages), 2):
            row_buttons = []
            for j in range(2):
                if i + j < len(truncated_messages):
                    msg = truncated_messages[i + j]
                    row_buttons.append(InlineKeyboardButton(msg, callback_data=f"search#{msg}"))
            keyboard.append(row_buttons)

        keyboard.append([
            InlineKeyboardButton("⛔️ Close", callback_data="close_data"),
            InlineKeyboardButton("◀️ Back", callback_data="home")
            ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit(f"<b>Here is the top searches of the day</b>", reply_markup=reply_markup, disable_web_page_preview=True)


    elif query.data.startswith("search#"):
        search = query.data.split("#")[1]
        await query.answer(text=f"Searching for your request :)")
        premium_status = await db.is_premium_status(query.from_user.id)
        if premium_status is True:
            text = await callback_paid_filter(search, query)
            await query.message.edit(text=f"<b>{text}</b>", reply_markup=None, disable_web_page_preview=True)
        else:    
            text = await callback_auto_filter(search, query)
            await query.message.edit(text=f"<b>{text}</b>", reply_markup=None, disable_web_page_preview=True)
 
    # get download button
    elif query.data.startswith("download#"):
        try:
            file_id = query.data.split("#")[1]
            msg = await client.send_cached_media(
                chat_id=BIN_CHANNEL,
                file_id=file_id)
            await client.send_message(
                text=f"<b>Requested By</b>:\n{query.from_user.mention} <code>{query.from_user.id}</code>\n<b>Link:</b>\n{URL}/watch/{msg.id}",
                chat_id=BIN_CHANNEL,
                disable_web_page_preview=True)
            online = f"{URL}/watch/{msg.id}"
            download = f"{URL}/download/{msg.id}"
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Watch", url=online),
                    InlineKeyboardButton("Download", url=download)
                    ],[
                    InlineKeyboardButton("⛔️ Close", callback_data='close_data')
                    ]]
            ))
        except Exception as e:
            await query.answer(f"Error:\n{e}", show_alert=True)     

    # generate redeem code
    elif query.data.startswith("redeem"):
        buttons = [[
            InlineKeyboardButton("1 Month", callback_data="Reedem#30")
            ],[
            InlineKeyboardButton("6 Months", callback_data="Reedem#180")
            ],[
            InlineKeyboardButton("12 Months", callback_data="Reedem#365")
            ]]
        await query.message.edit(
            f"<b>Choose the duration</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
    elif query.data.startswith("Reedem#"):
        duration = query.data.split("#")[1]
        buttons = [[
            InlineKeyboardButton("1 Redeem Code", callback_data=f"license#{duration}#1")
            ],[
            InlineKeyboardButton("5 Redeem Codes", callback_data=f"license#{duration}#5")
            ],[
            InlineKeyboardButton("10 Redeem Codes", callback_data=f"license#{duration}#10")
            ]]  
        await query.message.edit(f"<b>How many redeem codes you want?</b>", 
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )    
    elif query.data.startswith("license#"):
        duration, count = query.data.split("#")[1:]
        encoded_duration = base64.b64encode(str(duration).zfill(3).encode()).decode('utf-8').rstrip('=')

        codes_generated = []
        for _ in range(int(count)):
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://licensegen.onrender.com/?access_key={ACCESS_KEY}&action=generate&days=90") as resp:
                    if resp.status == 200:
                        json_response = await resp.json()
                        license_code = f"{json_response.get('license_code')[:10]}{encoded_duration}{json_response.get('license_code')[10:]}"
                        codes_generated.append(license_code)
                    else:
                        await query.answer(f"Error generating license code.{resp.status}", show_alert=True)
                        return
                
        codes_str = "\n".join(f"`{code}`" for code in codes_generated)
        await query.message.edit(f"<b>Redeem codes:</b>\n\n{codes_str}")

    #maintainance
    elif query.data == "maintenance":
        await toggle_config(query, "maintenance_mode", "Maintenance mode")
    elif query.data == "1link1file":
        await toggle_config(query, "one_link", "Single Ads in private")
    elif query.data == "1linkgroup":
        await toggle_config(query, "one_link_one_file_group", "Single Ads in group")
    elif query.data == "autoapprove":
        await toggle_config(query, "auto_accept", "Auto approve")
    elif query.data == "private_filter":
        await toggle_config(query, "private_filter", "Private filter")
    elif query.data == "group_filter":
        await toggle_config(query, "group_filter", "Group filter")
    elif query.data == "terms_and_condition":
        await toggle_config(query, "terms", "Terms&Condition")
    elif query.data == "spoll_check":
        await toggle_config(query, "spoll_check", "Spell Check")
    elif query.data == "force_subs":
        await toggle_config(query, "forcesub", "Force Subscribe")
    elif query.data == "no_ads":
        await toggle_config(query, "no_ads", "No Ads")

    elif query.data == "one_time_ads":
        button=[
            [InlineKeyboardButton("Single Ads in private ⚪️" if await mdb.get_configuration_value("one_link") else "Single Ads in private", callback_data="1link1file")],
            [InlineKeyboardButton("Single Ads in Group ⚪️" if await mdb.get_configuration_value("one_link_one_file_group") else "Single  Ads in Group", callback_data="1linkgroup")]
            ]
        reply_markup = InlineKeyboardMarkup(button)
        await query.message.edit(
            text=f"<b>Choose the option</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        
    elif query.data == "auto_filter_all":
        button=[
            [InlineKeyboardButton("Private Filter ⚪️" if await mdb.get_configuration_value("private_filter") else "Private Filter", callback_data="private_filter")],
            [InlineKeyboardButton("Group Filter ⚪️" if await mdb.get_configuration_value("group_filter") else "Group Filter", callback_data="group_filter")]
            ]
        reply_markup = InlineKeyboardMarkup(button)
        await query.message.edit(
            text=f"<b>Choose the option</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )      

    # Shortner button
    elif query.data == "shortner":
        shortnr = await mdb.get_configuration_value("shortner")
        buttons = [[
            InlineKeyboardButton("Shareus ⚪️" if shortnr == "shareus" else "Shareus", callback_data="shareus"),
            ],[
            InlineKeyboardButton("GPLinks ⚪️" if shortnr == "gplinks" else "GPLinks", callback_data="gplinks"),
            ],[
            InlineKeyboardButton("AdLinkfly ⚪️" if shortnr == "adlinkfly" else "AdLinkFly", callback_data="adlinkfly"),
            ],[
            InlineKeyboardButton("⛔️ Close", callback_data="close_data")
            ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit(
            text=f"<b>Choose the shortner</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        
    elif query.data == "shareus":
        await set_shortner(query, "shareus")
    elif query.data == "gplinks":
        await set_shortner(query, "gplinks")
    elif query.data == "adlinkfly":
        await set_shortner(query, "adlinkfly")   

    await query.answer('Share & Support Us♥️')

async def set_shortner(query, shortner):
    await mdb.update_configuration("shortner", shortner)
    await query.message.edit(f"<b>{shortner} shortner enabled.</b>", reply_markup=None)    

async def toggle_config(query, config_key, message):
    config = await mdb.get_configuration_value(config_key)
    if config is True:
        await mdb.update_configuration(config_key, False)
        await query.message.edit(f"<b>{message} disabled.</b>", reply_markup=None)
    else:
        await mdb.update_configuration(config_key, True)
        await query.message.edit(f"<b>{message} enabled.</b>", reply_markup=None)


async def delete_files(query, limit, file_type):
    k = await query.message.edit(text=f"Deleting <b>{file_type.upper()}</b> files...", reply_markup=None)
    files, _, _ = await get_search_results(file_type.lower(), max_results=limit, offset=0)
    deleted = 0

    for file in files:
        file_ids = file.file_id
        result = await Media.collection.delete_one({'_id': file_ids})

        if result.deleted_count:
            logger.info(f'{file_type.capitalize()} File Found! Successfully deleted from database.')

        deleted += 1

    deleted = str(deleted)
    await k.edit_text(text=f"<b>Successfully deleted {deleted} {file_type.upper()} files.</b>")  