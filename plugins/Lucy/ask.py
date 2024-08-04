# SPECIAL THANKS TO @Codeflix_Bots @erotixe @sd_bots FOR MODIFYING THESE AMAZING CODES 

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import requests
from info import LOG_CHANNEL, GOOGLE_API_KEY
import google.generativeai as genai

genai.configure(api_key=GOOGLE_API_KEY)

@Client.on_message(filters.command("ask") & filters.group)
async def ai_generate(client, message):
    user_input = message.text.split()[1:]

    if not user_input:
        await message.reply_text("<b>ʜᴇʟʟᴏ! ʜᴏᴡ ᴄᴀɴ ɪ ᴀssɪsᴛ ʏᴏᴜ ᴛᴏᴅᴀʏ?</b>")
        return

    user_input = " ".join(user_input)
    await client.send_message(LOG_CHANNEL, text=f"#google_ai ʀᴇǫᴜᴇsᴛ ғʀᴏᴍ {message.from_user.mention}\nǫᴜᴇʀʏ ɪs:- {user_input}")
    s = await message.reply_sticker("CAACAgUAAxkBAAECQNBmEPRJUuLrUDvpzQwsvs0KE1w5jgACcAQAAkdoOVaYU-q7wXAETB4E")
  
    if user_input.lower() in ["who is your owner", "what is your owner name"]:  
        buttons = [[
            InlineKeyboardButton("ɢʀᴏᴜᴘ", url="https://t.me/weebs_support")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_sticker("CAACAgUAAxkBAAECQNBmEPRJUuLrUDvpzQwsvs0KE1w5jgACcAQAAkdoOVaYU-q7wXAETB4E")
        await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}", reply_markup=reply_markup)
        return
        await s.delete()
      
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    prompt_parts = [user_input]
    response = model.generate_content(prompt_parts)
    response = model.generate_content(prompt_parts)
    await message.reply_text(f"<b>ʜᴇʏ {message.from_user.mention}\nǫᴜᴇʀʏ ɪs:- {user_input}\n\n{response.text}</b>")
    await client.send_message(LOG_CHANNEL, text=f"#google_ai ʀᴇǫᴜᴇsᴛ ғʀᴏᴍ {message.from_user.mention}\nǫᴜᴇʀʏ ɪs:- {user_input}")
    
@Client.on_message(filters.command("ask") & filters.private)
async def ai_generate_private(client, message):
  buttons = [[
    InlineKeyboardButton("ᴜsᴇ ɪɴ ɢʀᴏᴜᴘ", url="https://t.me/weebs_support")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_sticker("CAACAgUAAxkBAAECQNBmEPRJUuLrUDvpzQwsvs0KE1w5jgACcAQAAkdoOVaYU-q7wXAETB4E")
  await message.reply_text(text=f"<b>ʜᴇʏ {message.from_user.mention}\n\n» ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ꜰᴏʀ  ɢᴏᴏɢʟᴇ ᴀɪ :\n\n ɢᴏᴏɢʟᴇ ᴀɪ ᴄᴀɴ ᴀɴsᴡᴇʀ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴀɴᴅ sʜᴏᴡs ʏᴏᴜ ᴛʜᴇ ʀᴇsᴜʟᴛ\n\n ᴜsᴇ ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪɴ ɢʀᴏᴜᴘ</b>", reply_markup=reply_markup)



#- ᴄʀᴇᴅɪᴛ - Github - @Codeflix-bots , @erotixe, @sd_bots
#- ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛ..
#- ᴛʜᴀɴᴋ ʏᴏᴜ ᴄᴏᴅᴇғʟɪx ʙᴏᴛs ғᴏʀ ʜᴇʟᴘɪɴɢ ᴜs ɪɴ ᴛʜɪs ᴊᴏᴜʀɴᴇʏ 
#- ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ɢɪᴠɪɴɢ ᴍᴇ ᴄʀᴇᴅɪᴛ @Codeflix-bots  
#- ғᴏʀ ᴀɴʏ ᴇʀʀᴏʀ ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ -> ᴛᴇʟᴇɢʀᴀᴍ @codeflix_bots Community @Otakflix_Network </b>

