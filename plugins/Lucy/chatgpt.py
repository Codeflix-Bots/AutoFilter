import requests
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters, Client
from MukeshAPI import api

@Client.on_message(filters.command(["chatgpt", "ai", "hey", "ucy", "gpt"], prefixes=[".", "L", "l", "", "S", "/"]))
async def chat_gpt(bot, message):
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        
        # Check if name is defined, if not, set a default value
        name = message.from_user.first_name if message.from_user else "User"
        
        if len(message.command) < 2:
            await message.reply_text(f"**ʜᴇʟʟᴏ {name}, ʜᴏᴡ ᴄᴀɴ ɪ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏᴅᴀʏ?**")
        else:
            query = message.text.split(' ', 1)[1]
            response = api.gemini(query)["results"]
            await message.reply_text(f"{response}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"**Error: {e}**")
