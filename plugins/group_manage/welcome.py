import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import User, Message, Sticker, Document, ChatMember
import os 
from os import error
import logging
import pyrogram
import time
from decouple import config
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import User, Message, Sticker, Document, ChatMember

Client= Client(
    "Welcome-Bot",
     bot_token = os.environ["BOT_TOKEN"],
     api_id = int(os.environ["API_ID"]),
     api_hash = os.environ["API_HASH"]
)




    
@Client.on_message(filters.new_chat_members)
async def auto_welcome(bot, message):
    # from PR0FESS0R-99 import ID-Bot
    first = message.from_user.first_name
    last = message.from_user.last_name
    mention = message.from_user.mention
    username = message.from_user.username
    chat_id = int(message.chat.id)
    count = await Client.get_chat_members_count(chat_id)
    id = message.from_user.id
    group_name = message.chat.title
    group_username = message.chat.username
    name_button = "🔰 JOIN NOW 🔰"
    link_button = "t.me/team_netflix"
    button_name = os.environ.get("WELCOME_BUTTON_NAME", name_button)
    button_link = os.environ.get("WELCOME_BUTTON_LINK", link_button)
    welcome_text = f"Hey {mention}\nWelcome To {group_name} your admission no {count}"
    WELCOME_TEXT = os.environ.get("WELCOME_TEXT", welcome_text)
    print("Welcome Message Activate")
    BUTTON = bool(os.environ.get("WELCOME_BUTTON"))
    if not BUTTON:
       await message.reply_text(text=WELCOME_TEXT.format(
           chat_id = int(message.chat.id),
           count = await Client.get_chat_members_count(chat_id),
           first = message.from_user.first_name,
           last = message.from_user.last_name,
           username = None if not message.from_user.username else '@' + message.from_user.username,
           mention = message.from_user.mention,
           id = message.from_user.id,
           group_name = message.chat.title,
           group_username = None if not message.chat.username else '@' + message.chat.username
          )
       )
    else:
       await msg.reply_text(text=WELCOME_TEXT.format(
           chat_id = int(message.chat.id),
           count = await Client.get_chat_members_count(chat_id),
           first = message.from_user.first_name,
           last = message.from_user.last_name,
           username = None if not message.from_user.username else '@' + message.from_user.username,
           mention = msg.from_user.mention,
           id = message.from_user.id,
           group_name = message.chat.title,
           group_username = None if not message.chat.username else '@' + message.chat.username
          ),
       reply_markup=InlineKeyboardMarkup(
               [
                   [
                       InlineKeyboardButton
                           (
                               button_name, url=button_link
                           )
                   ]  
               ]
           )
       )  


print("""Auto Welcome Bot Started

Maintained By Team_netflix""")
