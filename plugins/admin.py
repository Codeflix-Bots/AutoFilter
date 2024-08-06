from pyrogram import Client, filters
from database.users_chats_db import db
import asyncio
from Script import script
from info import LOG_CHANNEL, AUTH_GROUPS, BIN_CHANNEL, URL, ADMINS, SUPPORT_GROUP
from utils import temp
import re
from datetime import datetime, timedelta
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ChatJoinRequest
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from database.ia_filterdb import get_search_results
from database.config_db import mdb


PATTERN_DOWNLOAD = re.compile(
    r"\bhow to (?:download|find|search for|get) (?:movie(?:s)?|series|link(?:s)?)\b",
    re.IGNORECASE
)
@Client.on_message(filters.regex(PATTERN_DOWNLOAD))
async def how2download(_, message):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("How To Download", url="https://t.me/QuickAnnounce/5")]])
    response_text = "<b>Please Watch This Video To Know How To Download Movies And Series From This Bot.</b>"
    await message.reply_text(response_text, reply_markup=keyboard, reply_to_message_id=message.id, disable_web_page_preview=True)

@Client.on_message(filters.private & filters.regex(r"^(hi+|hello+|hey+)$", re.IGNORECASE))
async def echo(_, message):
    response_text = f"<b>Hello</b>, {message.from_user.mention}!\n<b>Please Provide The Name Of The Movie Or Series You're Looking For, and I'll Help You To Find It..</b>"
    await message.reply_text(response_text, reply_to_message_id=message.id, disable_web_page_preview=True)

@Client.on_message(filters.media & ~filters.photo & filters.private & ~filters.user(ADMINS))
async def media_dl_filter(client, message):
    m=await message.reply_text("<b>Please Don't Send Any Files In My PM. It Will Be Deleted Within 1 Minute.</b>", reply_to_message_id=message.id)
    await asyncio.sleep(60)
    await message.delete()
    await m.delete()
    
@Client.on_edited_message(filters.private & ~filters.user(ADMINS) & ~filters.bot)
async def editmsg_filter(client, message):
    m = await message.reply_text(text="<b>Please Send a New Message Rather Than Editing The Existing One.</b>", reply_to_message_id=message.id)
    await asyncio.sleep(10)
    await m.delete()
    await message.delete()

# Add paid user to database and send message
@Client.on_message(filters.command('add_paid') & filters.user(ADMINS))
async def add_paid(client, message):
    try:
        if len(message.command) < 2:
            raise ValueError

        user_id = int(message.command[1])

        if len(message.command) > 2:
            duration = int(message.command[2])
            if not (1 <= duration <= 365):
                return await message.reply("Duration should be between 1 and 365 days.")
        else:
            duration = 30

        if len(message.command) > 3:
            date_str = message.command[3]
            provided_date = datetime.strptime(date_str, '%d/%m/%Y')
        else:
            provided_date = datetime.now()

        subscription_date= int(provided_date.timestamp())

        user = await client.get_users(user_id)
        name = user.first_name if not user.last_name else f"{user.first_name} {user.last_name}"

        if await db.is_premium_status(user_id):
            return await message.reply(f"**{name}** is already a premium user.")

        await db.add_user_as_premium(user_id, duration, subscription_date)
        await message.reply(f"Premium subscription added for **{name}** for {duration} days.")
        await client.send_message(user_id, f"Your subscription has been enabled for {duration} days.")
    except (ValueError, IndexError, ValueError):
        await message.reply("Invalid input. Please provide a valid user id, optionally a duration (1-365), and optionally a subscription date (dd/mm/yyyy).")

                
# remove paid user from database
@Client.on_message(filters.command('remove_paid') & filters.user(ADMINS))
async def remove_paid(client, message):
    if len(message.command) == 1:
        return await message.reply('Please provide a user id / username')
    chat = message.command[1]
    try:
        chat = int(chat)
    except ValueError:
        pass
    try:
        k = await client.get_users(chat)
    except IndexError:
        return await message.reply("This might be a channel, make sure it's a user.")
    else:
        await db.remove_user_premium(k.id)
        await message.reply(f"Successfully Removed Subscription for {k.first_name}")
        
        
#request command 
@Client.on_message(filters.command("request") & filters.private)
async def request(client, message):
    # Strip the command and normalize the movie name
    movie_name = message.text.replace("/request", "").replace("/Request", "").strip()
    files, _, _ = await get_search_results(movie_name.lower(), offset=0, filter=True)

    if not movie_name:
        await message.reply_text(script.REQM, disable_web_page_preview=True)
        return
    
    if files:
        await message.reply_text(f"**This Movie Is Already Available In Our Database. Please Send Movie Name Directly.**", reply_to_message_id=message.id, disable_web_page_preview=True)

    else:
        await message.reply_text(script.REQ_REPLY.format(movie_name), disable_web_page_preview=True)
        log_message = script.REQ_TEXT.format(temp.B_NAME, message.from_user.mention, message.from_user.id, movie_name)
        await client.send_message(LOG_CHANNEL, log_message, disable_web_page_preview=True)


# reset daily files count        
@Client.on_message(filters.command("resetdaily") & filters.user(ADMINS))
async def resetdaily(client, message):
    m = await message.reply_text("Resetting daily files count...")
    await db.reset_all_files_count()
    await m.edit("Successfully reset daily files count!")

#reset daily files count of user
@Client.on_message(filters.command("reset") & filters.user(ADMINS))
async def resetdailyuser(client, message):
    user_id = message.command[1]
    if len(message.command) < 2:
        return await message.reply("Please provide a user id / username")
    m = await message.reply_text("Resetting daily files count of user...")
    await asyncio.sleep(2)
    success = await db.reset_daily_files_count(user_id)
    if success:
        await m.edit("Successfully reset daily files count of user!")
    else:
        await m.edit("Failed to reset daily files count of user!")    

# remove all premium user from database
@Client.on_message(filters.command("remove_all_premium") & filters.user(ADMINS))
async def remove_all_premium(client, message):
    m = await message.reply_text("Removing all premium users...")
    await db.remove_all_premium_users()
    await m.edit("Successfully removed all premium users!")

# remove all free user from database
@Client.on_message(filters.command("remove_all_free") & filters.user(ADMINS))
async def remove_all_free(client, message):
    m = await message.reply_text("Removing all free users...")
    await db.remove_all_free_users()
    await m.edit("Successfully removed all free users!")

# list down all premium user from database
@Client.on_message(filters.command("premiumlist") & filters.user(ADMINS))
async def list_premium(client, message):
    m = await message.reply_text("Listing all premium users...")
    count = await db.total_premium_users_count()
    out = f"**List of Premium Users: - {count}**\n\n"
    users = await db.get_all_premium_users()
    async for user in users:
        user_id = user.get("id")
        userx = await client.get_users(user_id)
        user_name = userx.first_name if not userx.last_name else f"{userx.first_name} {userx.last_name}"
        duration = user.get("premium_expiry")
        purchase_date_unix = user.get("purchase_date")
        purchase_date = datetime.fromtimestamp(purchase_date_unix)
        purchase_date_str = purchase_date.strftime("%d/%m/%Y")
        out += f"ID: `{user_id}`\nName: {user_name}\nPurchase On:\n`{purchase_date_str}`\nDuration: `{duration}` days\n\n"
    try:
        await m.edit(out, disable_web_page_preview=True)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption=f"List Of Users - Total {count} Users")


@Client.on_message(filters.command(['user', 'info', 'plan']))
async def userinfo(client, message):

    if len(message.command) < 2:
        user_id = message.from_user.id
    else:    
        user_id = int(message.command[1])

    try:
        user = await client.get_users(user_id)
    except ValueError:
        await message.reply_text("Invalid user ID provided.")
        return

    user_name = user.first_name if not user.last_name else f"{user.first_name} {user.last_name}"
    user_link = f"<a href='tg://user?id={user_id}'>{user_name}</a>"

    private_joined = await db.is_user_joined(user_id)
    premium= await db.is_premium_status(user_id)
    users = await db.get_user(user_id)
    total_files_sent = users.get("lifetime_files") or "N/A"
    dc_id = user.dc_id or "Invalid DP"
    refferal = await db.fetch_value(user_id, "refferal")
    today_recieved = users.get("files_count") or "N/A"

    if premium:
        duration = users.get("premium_expiry")
        purchase_date_unix = users.get("purchase_date")

        status = "Premium (Paid)"
        if duration == 28:
            status = "Premium (Referral)"
        if duration == 29:
            status = "Premium (Promocode)"

        purchase_date = datetime.fromtimestamp(purchase_date_unix)
        expiry_date = purchase_date + timedelta(days=duration)
        purchase_date_str = purchase_date.strftime("%d/%m/%Y")
        expiry_date_str = expiry_date.strftime("%d/%m/%Y")
        days_left = (expiry_date - datetime.now()).days

    else:
        status = "Free"
        purchase_date_str = "N/A"
        expiry_date_str = "N/A"
        days_left = "N/A"
        duration = "N/A"

    # Create the message with the information and keyboard.
    message_text = (
        f"<b>➲User ID:</b> <code>{user_id}</code>\n"
        f"<b>➲Name:</b> {user_link}\n"
        f"<b>➲DC ID:</b> {dc_id}\n"
        f"<b>➲Subscribed:</b> {private_joined}\n"
        f"<b>➲Status:</b> {status}\n"
        f"<b>➲Purchase Date:</b> <code>{purchase_date_str}</code>\n"
        f"<b>➲Expiry Date:</b> <code>{expiry_date_str}</code>\n"
        f"<b>➲Days Left:</b> <code>{days_left}/{duration}</code> days\n"
        f"<b>➲Refferal Points:</b> <code>{refferal}</code>\n"
        f"<b>➲Total Recieved:</b> <code>{total_files_sent}</code>\n"
        f"<b>➲Today Recieved:</b> <code>{today_recieved}</code>\n"
    )

    await message.reply_text(
        text=message_text,
        disable_web_page_preview=True
    )


@Client.on_message(filters.command(['upgrade', 'premium']))
async def upgrademsg(_, message):
    buttons = [[
                InlineKeyboardButton('💫 Confirm', callback_data="confirm"),
                InlineKeyboardButton('◀️ Back', callback_data="home")
            ]]
    tnc= f"<a href=https://t.me/{temp.U_NAME}?start=terms>T&C apply</a>"
    await message.reply(
        text=script.REMADS_TEXT.format(tnc),
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        )

# optional command to list all commands
@Client.on_message(filters.command("commands") & filters.user(ADMINS))
async def allcommands(client, message):
    await message.reply_text(
        f"<b>Commands:</b>\n"
        f"<b>➲/stats</b> - To get bot stats\n"
        f"<b>➲/admin</b> - Admin panel\n"
        f"<b>➲/info</b> - To get user info\n"
        f"<b>➲/premiumlist</b> - To list all premium users\n"
        f"<b>➲/resetdaily</b> - To reset daily files count\n"
        f"<b>➲/add_paid</b> - To add a user as premium\n"
        f"<b>➲/remove_paid</b> - To remove a user from premium\n"
        f"<b>➲/broadcast</b> - To broadcast a message to all users\n"
        f"<b>➲/license</b> - To get redeem code\n"
        f"<b>➲/revoke</b> - To revoke redeem code\n"
        f"<b>➲/invite</b> - To get invite link of a chat\n"
        f"<b>➲/ban</b> - To ban a user\n"
        f"<b>➲/unban</b> - To unban a user\n"
        )
    
# Add functions for refferal system
@Client.on_message(filters.command("refer"))
async def reffer(_, message):
    m = await message.reply_text(f"<b>Generating Your Refferal Link...</b>")
    await asyncio.sleep(2)
    user_id = message.from_user.id
    referral_points = await db.fetch_value(user_id, "refferal")
    refferal_link = f"https://t.me/{temp.U_NAME}?start=ReferID-{user_id}"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Invite Your Friends", url=f"https://telegram.me/share/url?url={refferal_link}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83")]])
    await m.edit(f"<b>Here is your refferal link:\n\n{refferal_link}\n\nShare this link with your friends, Each time they join, Both of you will be rewarded 10 refferal points and after 50 points you will get 1 month premium subscription.\n\n Referral Points: {referral_points}</b>",
                 reply_markup=keyboard,
                 disable_web_page_preview=True)
    
@Client.on_message(filters.command("redeem"))
async def redeem_req(_, message):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Purchase Now", callback_data="remads")]])
    await message.reply(
        text=f"<b>Kindly Provide The Redeem Code For Premium Activation.\n\nIf You Don't Have a Redeem Code, You Can Purchase One Here.</b>",
        reply_markup=keyboard
    )

@Client.on_message(filters.command('top'))
async def top(_, message):

    def is_alphanumeric(string):
        return bool(re.match('^[a-zA-Z0-9 ]*$', string))
    
    try:
        limit = int(message.command[1])
    except (IndexError, ValueError):
        limit = 20

    top_messages = await mdb.get_top_messages(limit)

    # Use a set to ensure unique messages (case sensitive).
    seen_messages = set()
    truncated_messages = []

    for msg in top_messages:
        # Check if message already exists in the set (case sensitive)
        if msg.lower() not in seen_messages and is_alphanumeric(msg):
            seen_messages.add(msg.lower())
            
            if len(msg) > 35:
                truncated_messages.append(msg[:35 - 3])
            else:
                truncated_messages.append(msg)

    keyboard = []
    for i in range(0, len(truncated_messages), 2):
        row = truncated_messages[i:i+2]
        keyboard.append(row)
    
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True, placeholder="Most searches of the day")
    await message.reply_text(f"<b>Top searches of the day</b>", reply_markup=reply_markup)

@Client.on_message(filters.command('latest'))
async def latests(_, message):

    def is_valid_string(string):
        return bool(re.match('^[a-zA-Z0-9 ]*$', string))
    
    try:
        limit = int(message.command[1])
    except (IndexError, ValueError):
        limit = 20

    m = await message.reply_text(f"<b>Please wait, fetching latest searches...</b>")
    top_messages = await mdb.get_top_messages(limit)

    unique_messages = set()
    truncated_messages = []

    for msg in top_messages:
        if msg.lower() not in unique_messages and is_valid_string(msg):
            unique_messages.add(msg.lower())
            if len(msg) > 30:
                truncated_messages.append(msg[:30 - 3].lower().title() + "...")  # Convert to lowercase and add to list
            else:
                truncated_messages.append(msg.lower().title())  # Convert to lowercase and add to list

    keyboard = []
    for i in range(0, len(truncated_messages), 2):
        row = truncated_messages[i:i+2]
        keyboard.append(row)

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, placeholder="Most searches of the day")
    await message.reply_text(f"<b>Here are the top searches of the day</b>", reply_markup=reply_markup)
    await m.delete()


# auto approve members 
@Client.on_chat_join_request((filters.group | filters.channel) & filters.chat(AUTH_GROUPS) if AUTH_GROUPS else (filters.group | filters.channel))
async def autoapprove(client: Client, message: ChatJoinRequest):
    chat=message.chat
    user=message.from_user
    APPROVE = await mdb.get_configuration_value("auto_accept")
    try:
        if APPROVE is not None and APPROVE is True:
            await client.approve_chat_join_request(chat.id, user.id)
            await client.send_message(chat_id=chat.id, text=f"<b>Hello {user.mention}, Welcome To {chat.title}</b>")
    except Exception as e:
        print(e)


@Client.on_message(filters.private & filters.command("stream"))
async def reply_stream(client, message):
    reply_message = message.reply_to_message

    if not reply_message or not (reply_message.document or reply_message.video):
        return await message.reply_text("**Reply to a video or document file.**")

    file_id = reply_message.document or reply_message.video

    try:
        msg = await reply_message.forward(chat_id=BIN_CHANNEL)
        await client.send_message(text=f"<b>Requested By</b>:{message.from_user.mention}  <code>{message.from_user.id}</code>",
                                  chat_id=BIN_CHANNEL,
                                  disable_web_page_preview=True)
    except Exception as e:
        return await message.reply_text(f"Error: {str(e)}")

    online_url = f"{URL}/watch/{msg.id}"
    download_url = f"{URL}/download/{msg.id}"

    file_name = file_id.file_name.replace("_", " ").replace(".mp4", "").replace(".mkv", "").replace(".", " ")

    await message.reply_text(
        text=f"<b>Here Is Your Streamable Link\n\nFile Name</b>:\n<code>{file_name}</code>\n\n<b>Powered By - @{SUPPORT_GROUP}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Watch", url=online_url),
                    InlineKeyboardButton("Download", url=download_url)
                ]
            ]
        ),
        disable_web_page_preview=True
    )


@Client.on_message(filters.command("admin", prefixes='@') & filters.private)
async def send_message_to_admin(client, message):

    if message.reply_to_message is None:
            return await message.reply("Please reply to a message with the @admin.")
    try:
        msg = message.reply_to_message
        admin_id = 2141736280
        user_id = message.from_user.id
        media = msg.photo or msg.video or msg.document
        caption = f"**New Message:**\n\n**Name:** {message.from_user.mention}\n**User ID:** `{user_id}`\n\n**Message:**\n\n{msg.text if msg.text else msg.caption}"

        if user_id in ADMINS:
            return await message.reply("You are an admin; you can't use this command.")
        
        if media:
            await client.send_cached_media(chat_id=admin_id, file_id=media.file_id, caption=caption)
        elif msg.text:
            await client.send_message(text=caption, chat_id=admin_id)

        await message.reply(f"Your message has been submitted to the admin, admin will reply you soon.\n**(Spam=Ban)**")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")
 

@Client.on_message(filters.command("send") & filters.private & filters.user(ADMINS))
async def send_message_to_user(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply("Please provide a user id.")

        user_id = message.command[1]
        user = await client.get_users(user_id)

        if not user:
            return await message.reply("Invalid user id")

        if message.from_user.id not in ADMINS:
            return await message.reply("You are not authorized to use this command.")

        msg = message.reply_to_message

        if not msg:
            return await message.reply("Please reply to a message.")

        media = msg.photo or msg.video or msg.document
        caption = msg.caption or "None"

        if media:
            await client.send_cached_media(chat_id=user_id, file_id=media.file_id, caption=caption)
        elif msg.text:
            await client.send_message(text=msg.text, chat_id=user_id)

        await message.reply(f"**Message sent to {user.first_name} successfully.**")    

    except ValueError as ve:
        await message.reply(f"Error: {str(ve)}")
    except Exception as e:
        await message.reply(f"An unexpected error occurred: {str(e)}")

@Client.on_message(filters.command("admin") & filters.user(ADMINS))
async def admin_controll(client, message):
    buttons_config_with_mdb = [
        # mdb key, text, alt_text, callback
        ("terms", "Terms ⚪️", "Terms", "terms_and_condition"),
        ("auto_accept", "Auto Approve ⚪️", "Auto Approve", "autoapprove"),
        ("maintenance_mode", "Maintainence ⚪️", "Maintainence", "maintenance"),
        ("spoll_check", "Spell Check ⚪️", "Spell Check", "spoll_check"),
        ("forcesub", "Force Subscribe ⚪️", "Force Subscribe", "force_subs"),
        ("no_ads", "No Ads ⚪️", "No Ads", "no_ads"),
    ]

    buttons_config_without_mdb = [
        ("1 Time Ads", "one_time_ads"),
        ("Auto Filter", "auto_filter_all"),
        ("Shortner", "shortner"),
        ("DeleteFiles", "delback"),
        ("Redeem Code", "redeem"),
        ("⛔️ Close", "close_data")
    ]

    button = []

    for i in range(0, len(buttons_config_with_mdb), 2):
        button_row = []
        for key, text, alt_text, callback in buttons_config_with_mdb[i:i+2]:
            config_value = await mdb.get_configuration_value(key)
            button_row.append(InlineKeyboardButton(text if config_value else alt_text, callback_data=callback))
        button.append(button_row)

    for i in range(0, len(buttons_config_without_mdb), 2):
        button_row = [InlineKeyboardButton(text, callback_data=callback) for text, callback in buttons_config_without_mdb[i:i+2]]
        button.append(button_row)

    await message.reply_text(
        text="**Admin Control Panel**",
        reply_markup=InlineKeyboardMarkup(button),
        disable_web_page_preview=True
    )