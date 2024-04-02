from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from plugins.helper.admin_check import admin_check
from plugins.helper.extract import extract_time, extract_user                               
from utils import temp 
from info import LOG_CHANNEL

@Client.on_message(filters.command("mute"))
async def mute_user(bot, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return
    user_id, user_first_name = extract_user(message)
    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions(
            )
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "👍🏻 "
                f"{user_first_name}"
                " Lavender's mouth is shut! 🤐"
            )
            await bot.send_message(LOG_CHANNEL, text=f"**MUTE**\n\n**USER**: <a href='tg://user?id={user_id}'>{user_first_name}</a> \n\n**USER ID**:`{user_id}`\n\n**PERMISSIONS: MUTED**\n\nin **CHAT NAME**: {message.chat.title}\n**CHAT ID** `{message.chat.id}`\n\n\n**POWERD BY:** {temp.B_LINK}")
        else:
            await message.reply_text(
                "👍🏻 "
                f"<a href='tg://user?id={user_id}'>"
                f"{user_first_name}"
                "</a>"
                " The mouth is closed! 🤐"
            )
            await bot.send_message(LOG_CHANNEL, text=f"**MUTE**\n\n**USER**: <a href='tg://user?id={user_id}'>{user_first_name}</a>\n\n**USER ID**:`{user_id}`\n\n**PERMISSIONS: MUTED**\n\nin **CHAT NAME**: {message.chat.title}\n**CHAT ID** `{message.chat.id}`\n\n\n**POWERD BY:** {temp.B_LINK}")
        


@Client.on_message(filters.command("tmute"))
async def temp_mute_user(bot, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return

    if not len(message.command) > 1:
        return

    user_id, user_first_name = extract_user(message)

    until_date_val = extract_time(message.command[1])
    if until_date_val is None:
        await message.reply_text(
            (
                "Invalid time type specified. "
                "Expected m, h, or d, Got it: {}"
            ).format(
                message.command[1][-1]
            )
        )
        return

    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions(
            ),
            until_date=until_date_val
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "Be quiet for a while! 😠"
                f"{user_first_name}"
                f" muted for {message.command[1]}!"
            )
            await bot.send_message(LOG_CHANNEL, text=f"**MUTE**\n\n**USER**: <a href='tg://user?id={user_id}'>{user_first_name}</a>\n\n**USER ID**:`{user_id}`\n\n**PERMISSIONS: MUTED**\n\nin **CHAT NAME**: {message.chat.title}\n**CHAT ID** `{message.chat.id}`\n\n\n**POWERD BY:** {temp.B_LINK}")
        else:
            await message.reply_text(
                "Be quiet for a while! 😠"
                f"<a href='tg://user?id={user_id}'>"
                f"{user_first_name}"
                "</a>"
                " Mouth "
                f" muted for {message.command[1]}!"
            )
            await bot.send_message(LOG_CHANNEL, text=f"**MUTE**\n\n**USER**: <a href='tg://user?id={user_id}'>{user_first_name}</a>\n\n**USER ID**:`{user_id}`\n\n**PERMISSIONS: MUTED**\n\nin **CHAT NAME**: {message.chat.title}\n**CHAT ID** `{message.chat.id}`\n\n\n**POWERD BY:** {temp.B_LINK}")
        
