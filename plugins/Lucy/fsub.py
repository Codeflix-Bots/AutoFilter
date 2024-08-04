from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import *


async def get_fsub(bot, message):
    target_channel_id = AUTH_CHANNEL  # Your channel ID
    user_id = message.from_user.id
    try:
        await bot.get_chat_member(target_channel_id, user_id)
    except UserNotParticipant:
        channel_link = (await bot.get_chat(target_channel_id)).invite_link
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇs", url=channel_link)
        keyboard = [[join_button]]
        await message.reply(
            f"<b>Dᴇᴀʀ Usᴇʀ {message.from_user.mention}!\n\nPʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ ! 😊\n\nDᴜᴇ ᴛᴏ sᴇʀᴠᴇʀ ᴏᴠᴇʀʟᴏᴀᴅ, ᴏɴʟʏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ sᴜʙsᴄʀɪʙᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ʙᴏᴛ !</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return False
    else:
        return True
