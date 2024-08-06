import os
import logging
import asyncio
from datetime import datetime, timedelta
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from database.config_db import mdb
from info import CHANNELS, ADMINS, FORCESUB_CHANNEL, WAIT_TIME, SUPPORT_GROUP, SUPPORT_CHANNEL
from utils import is_subscribed, temp, replace_blacklist
import re
import base64
import pytz
logger = logging.getLogger(__name__)

BATCH_FILES = {}
blacklist = script.BLACKLIST
waitime = WAIT_TIME

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('Channel', url=f"https://t.me/{SUPPORT_CHANNEL}"),
                InlineKeyboardButton('Group', url=f"https://t.me/{SUPPORT_GROUP}")
            ]
            ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
        await asyncio.sleep(2)
    term = await mdb.get_configuration_value("terms")
    if not await db.is_user_exist(message.from_user.id) and term and len(message.command) != 2:
        button = [
            [InlineKeyboardButton("📜 Read Terms", callback_data="terms")],
            [InlineKeyboardButton("✅ Accept", callback_data="home")]
            
        ]
        reply_markup = InlineKeyboardMarkup(button)
        await message.reply(
            f"<b>Welcome to our {temp.B_NAME} Bot! Before using our service, you agree to these Terms & Conditions.Please read them carefully.</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        return

    if len(message.command) != 2:
        buttons = [[
                    InlineKeyboardButton('📎 Refer', callback_data="refer"),
                    InlineKeyboardButton('🔥 Top Search', callback_data="topsearch")
                    ],[
                    InlineKeyboardButton('🎟️ Upgrade ', callback_data="remads"),
                    InlineKeyboardButton('🗣️ Request', callback_data="request")
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=script.START_TXT.format(message.from_user.mention, temp.B_NAME),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        return
    data = message.command[1]
    forcesub = await mdb.get_configuration_value("forcesub")
    if not data.split("-", 1)[0] == "ReferID" and FORCESUB_CHANNEL and forcesub and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(FORCESUB_CHANNEL), creates_join_request=True)
        except Exception as e:
            logger.error(e)
        btn = [
            [
                InlineKeyboardButton(
                    "Join", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton("Try Again", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("Try Again", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**Only Channel Subscriber Can Use This Bot**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "upgrade", "help"]:
        buttons = [[
                InlineKeyboardButton('💫 Confirm', callback_data="confirm"),
                InlineKeyboardButton('◀️ Back', callback_data="home")
                ]]
        tnc= f"<a href=https://t.me/{temp.U_NAME}?start=terms>T&C apply</a>"
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=script.REMADS_TEXT.format(tnc),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        return
    
    if message.command[1] == "terms":
        button = [[InlineKeyboardButton('⛔️ Close', callback_data="close_data")]]
        await message.reply_text(text=script.TERMS, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)
        return
    
    # showing ads
    if message.command[1] == "ads":
        msg, _, impression = await mdb.get_advirtisment()
        user = await db.get_user(message.from_user.id)
        seen_ads = user.get("seen_ads")
        if msg is not None:
            await message.reply_text(text=f"{msg}\n<b>#Ads</b>", disable_web_page_preview=True)
            if impression is not None and seen_ads is not True:
                await mdb.update_advirtisment_impression(int(impression) - 1)
                await db.update_value(message.from_user.id, "seen_ads", True)
        else:
            await message.reply(f"<b>No Ads Found</b>")
        await mdb.reset_advertisement_if_expired()
        if msg is None and seen_ads is True:
            await db.update_value(message.from_user.id, "seen_ads", False)
        return
        
    if message.command[1] == "topsearch":
        m = await message.reply_text(f"<b>Please Wait, Fetching Top Searches...</b>")
        top_messages = await mdb.get_top_messages(30)

        truncated_messages = set()  # Use a set instead of a list
        for msg in top_messages:
            if len(msg) > 30:
                truncated_messages.add(msg[:30 - 3].lower().title() + "...")  # Convert to lowercase, capitalize and add to set
            else:
                truncated_messages.add(msg.lower().title())  # Convert to lowercase, capitalize and add to set

        keyboard = []
        for i in range(0, len(truncated_messages), 2):
            row = list(truncated_messages)[i:i+2]  # Convert set to list for indexing
            keyboard.append(row)
    
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, placeholder="Most searches of the day")
        await message.reply_text(f"<b>Here Is The Top Searches Of The Day</b>", reply_markup=reply_markup)
        await m.delete()
        return
    
    # Refer
    if message.command[1] == "refer":
        m = await message.reply_text(f"<b>Generating Your Refferal Link...</b>")
        user_id = message.from_user.id
        referral_points = await db.fetch_value(user_id, "referral")
        refferal_link = f"https://t.me/{temp.U_NAME}?start=ReferID-{user_id}"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Invite Your Friends", url=f"https://telegram.me/share/url?url={refferal_link}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83")]])
        await m.edit(f"<b>Here is your refferal link:\n\n{refferal_link}\n\nShare this link with your friends, Each time they join, Both of you will be rewarded 10 refferal points and after 50 points you will get 1 month premium subscription.\n\n Referral Points: {referral_points}</b>",
                     reply_markup=keyboard,
                     disable_web_page_preview=True
        )
        return
    

    # for counting each files for user
    files_counts = await db.fetch_value(message.from_user.id, "files_count") or 0
    lifetime_files = await db.fetch_value(message.from_user.id, "lifetime_files")
    # optinal function for checking time difference between currrent time and next 12'o clock
    kolkata = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.now(kolkata)
    next_day = current_datetime + timedelta(days=1)
    next_day_midnight = datetime(next_day.year, next_day.month, next_day.day, tzinfo=kolkata)
    time_difference = (next_day_midnight - current_datetime).total_seconds() / 3600
    time_difference = round(time_difference)


    data = message.command[1].strip()
    if data.startswith(f"{temp.U_NAME}"):
        _, rest_of_data = data.split('-', 1)
        encypted_user_id, file_id = rest_of_data.split('_', 1)
        user_id_bytes = base64.urlsafe_b64decode(encypted_user_id)  # Decode from URL-safe base64
        userid = user_id_bytes.decode('utf-8')  # Convert bytes back to string
        print(userid)
        
        files_ = await get_file_details(file_id)

        if not files_:
            return await message.reply(f"<b>No such file exists.</b>")

        if userid != str(message.from_user.id):
            return await message.reply(f"<b>You can't access someone else's request, request your own.</b>")
        
        files = files_[0]
        premium_status = await db.is_premium_status(message.from_user.id)
        button = [[
            InlineKeyboardButton("Search", url=f"https://t.me/{temp.U_NAME}"),
            InlineKeyboardButton('Request', url=f"https://t.me/+yea6oolZNRpjZjBl")
            ]]
        if premium_status is True:
            button.append([InlineKeyboardButton("Watch & Download", callback_data=f"download#{file_id}")])
            
        if premium_status is not True and files_counts is not None and files_counts >= 15:
                return await message.reply(f"<b>You Have Exceeded Your Daily Limit. Please Try After {time_difference} Hours, or  <a href=https://t.me/{temp.U_NAME}?start=upgrade>Upgrade</a> To Premium For Unlimited Request.</b>", disable_web_page_preview=True)
        
        media_id = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f"<code>{await replace_blacklist(files.caption or files.file_name, blacklist)}</code>\n@{SUPPORT_CHANNEL}",
            reply_markup=InlineKeyboardMarkup(button)
            )
        
        await db.update_value(message.from_user.id, "files_count", files_counts + 1)
        await db.update_value(message.from_user.id, "lifetime_files", lifetime_files + 1)
        del_msg = await client.send_message(
            text=f"<b>File will be deleted in 10 mins. Save or forward immediately.</b>",
            chat_id=message.from_user.id,
            reply_to_message_id=media_id.id)
        
        await asyncio.sleep(waitime or 600)
        await media_id.delete()
        return await del_msg.edit("__⊘ This message was deleted__")


    # Referral sysytem
    elif data.split("-", 1)[0] == "ReferID":
        invite_id = int(data.split("-", 1)[1])

        try:
            invited_user = await client.get_users(invite_id)
        except Exception as e:
            print(e)
            return

        if str(invite_id) == str(message.from_user.id):
            inv_link = f"https://t.me/{temp.U_NAME}?start=ReferID-{message.from_user.id}"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Invite Your Friends", url=f"https://telegram.me/share/url?url={inv_link}&text=%F0%9D%90%87%F0%9D%90%9E%F0%9D%90%A5%F0%9D%90%A5%F0%9D%90%A8!%20%F0%9D%90%84%F0%9D%90%B1%F0%9D%90%A9%F0%9D%90%9E%F0%9D%90%AB%F0%9D%90%A2%F0%9D%90%9E%F0%9D%90%A7%F0%9D%90%9C%F0%9D%90%9E%20%F0%9D%90%9A%20%F0%9D%90%9B%F0%9D%90%A8%F0%9D%90%AD%20%F0%9D%90%AD%F0%9D%90%A1%F0%9D%90%9A%F0%9D%90%AD%20%F0%9D%90%A8%F0%9D%90%9F%F0%9D%90%9F%F0%9D%90%9E%F0%9D%90%AB%F0%9D%90%AC%20%F0%9D%90%9A%20%F0%9D%90%AF%F0%9D%90%9A%F0%9D%90%AC%F0%9D%90%AD%20%F0%9D%90%A5%F0%9D%90%A2%F0%9D%90%9B%F0%9D%90%AB%F0%9D%90%9A%F0%9D%90%AB%F0%9D%90%B2%20%F0%9D%90%A8%F0%9D%90%9F%20%F0%9D%90%AE%F0%9D%90%A7%F0%9D%90%A5%F0%9D%90%A2%F0%9D%90%A6%F0%9D%90%A2%F0%9D%90%AD%F0%9D%90%9E%F0%9D%90%9D%20%F0%9D%90%A6%F0%9D%90%A8%F0%9D%90%AF%F0%9D%90%A2%F0%9D%90%9E%F0%9D%90%AC%20%F0%9D%90%9A%F0%9D%90%A7%F0%9D%90%9D%20%F0%9D%90%AC%F0%9D%90%9E%F0%9D%90%AB%F0%9D%90%A2%F0%9D%90%9E%F0%9D%90%AC.")]])
            await message.reply_text(f"<b>You Can't Invite Yourself, Send This Invite Link To Your Friends\n\nInvite Link</b> - \n<code>{inv_link}</code>",
                                    reply_markup=keyboard,
                                    disable_web_page_preview=True)
            return

        if not await db.is_user_exist(message.from_user.id):
            try:
                await db.add_user(message.from_user.id, message.from_user.first_name)
                await asyncio.sleep(1)
                referral = await db.fetch_value(invite_id, "referral") 
                await db.update_value(invite_id, "referral", referral + 10) 
                await asyncio.sleep(1)
                referral_count = await db.fetch_value(message.from_user.id, "referral")
                await db.update_value(message.from_user.id, "referral", referral_count + 10)
                await client.send_message(text=f"You have successfully Invited {message.from_user.mention}", chat_id=invite_id)
                await message.reply_text(f"You have been successfully invited by {invited_user.first_name}", disable_web_page_preview=True)
            except Exception as e:
                print(e)
        else:
            await message.reply_text("You already Invited or Joined")
        return
        
    try:
        data = message.command[1].strip()
        try:
            pre, file_id = data.split('_', 1)
        except:
            file_id = data
            pre = ""

        files_ = await get_file_details(file_id)   
        if not files_:
            file_id = None
            try:
                pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("utf-16")).split("_", 1)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                )
                filetype = msg.media
                file = getattr(msg, filetype)
                title = file.file_name
                f_caption = f"<code>{title}</code>"
                await msg.edit_caption(f_caption)
                return
            except Exception as e:
                await message.reply(f'Error processing file: {e}')
            return await message.reply('No such file exist.')

        files = files_[0]
        title = files.file_name
        premium_status = await db.is_premium_status(message.from_user.id)
        button = [[
            InlineKeyboardButton("Search", url=f"https://t.me/{temp.U_NAME}"),
            InlineKeyboardButton('Request', url=f"https://Telegram.me/{SUPPORT_GROUP}")
            ]]
        if premium_status is True:
            button.append([InlineKeyboardButton("Watch & Download", callback_data=f"download#{file_id}")])

        media_id = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,

            caption=f"<code>{await replace_blacklist(files.caption or files.file_name, blacklist)}</code>\n@{SUPPORT_CHANNEL}",
            reply_markup=InlineKeyboardMarkup(button)
            )
    
        # for counting each files for user
        files_counts = await db.fetch_value(message.from_user.id, "files_count") or 0
        lifetime_files = await db.fetch_value(message.from_user.id, "lifetime_files")
        await db.update_value(message.from_user.id, "files_count", files_counts + 1)
        await db.update_value(message.from_user.id, "lifetime_files", lifetime_files + 1)

        del_msg = await client.send_message(
            text=f"<b>File will be deleted in 10 mins. Save or forward immediately.</b>",
            chat_id=message.from_user.id,
            reply_to_message_id=media_id.id)
    
        await asyncio.sleep(waitime or 600)
        await media_id.delete()
        return await del_msg.edit("__⊘ This message was deleted__")
    except Exception as e:
        logger.error(e)

        
@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return
    
    file_id, _ = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('File is successfully deleted from database')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File is successfully deleted from database')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteallfiles') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Hell No", callback_data="close_data"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Yes", callback_data="autofilter_delete"
                    )
                ],

                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def delete_multiple_files(bot, message):
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

    await message.reply_text(
        text="<b>Select The Type Of Files You Want To Delete..?</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.message.edit('Succesfully Deleted All The Indexed Files.')