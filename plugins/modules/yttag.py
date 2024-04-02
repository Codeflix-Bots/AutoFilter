import os
import pyrogram
from pyrogram import Client
from pyrogram import filters
from youtubesearchpython import VideosSearch
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import User, Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
import YoutubeTags # https://pypi.org/project/youtubetags
from YoutubeTags import videotags

BTNS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('ꜱᴜʙꜱᴄʀɪʙᴇ ᴍʏ ᴄʜᴀɴɴᴇʟ', url='https://t.me/team_netflix')
        ]
    ]
)

@Client.on_message(filters.command("yttags"))
async def yttags(bot, message):
    if not message.reply_to_message:
        return await message.reply_text("**ʀᴇᴘʟʏ ᴡɪᴛʜ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ**")
    if not message.reply_to_message.text:
        return await message.reply_text("**ʀᴇᴘʟʏ ᴡɪᴛʜ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ**")
    link = message.reply_to_message.text
    tags = videotags(link)
    if tags=="":
         await message.reply_text("ɴᴏ ᴛᴀɢꜱ ꜰᴏᴜɴᴅ")
    else:
         await message.reply_text(text=f"**ɪ ꜰᴏᴜɴᴅ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴛᴀɢꜱ**\n\n`{tags}` ",reply_markup=BTNS)
