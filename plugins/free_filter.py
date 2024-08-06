import re
import math
import time
import base64
from Script import script
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from database.users_chats_db import db
from pyrogram.errors import MessageNotModified
from utils import get_size, replace_blacklist, temp
from database.ia_filterdb import get_search_results
from plugins.shortner import urlshare



BUTTONS = {}
SPELL_CHECK = {}

@Client.on_callback_query(filters.regex(r"^free"))
async def free_next_page(bot, query):
    _, req, key, offset = query.data.split("_")
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
        user_id = query.from_user.id
        user_id_bytes = str(user_id).encode('utf-8')  # Convert to bytes
        urlsafe_encoded_user_id = base64.urlsafe_b64encode(user_id_bytes).decode('utf-8') 
        shortlink = await urlshare(f"https://telegram.me/{temp.U_NAME}?start={temp.U_NAME}-{urlsafe_encoded_user_id}_{file.file_id}")
        file_link = f"🎬 [{get_size(file.file_size)} | {await replace_blacklist(file.file_name, script.BLACKLIST)}]({shortlink})"
        search_results_text.append(file_link)

    search_results_text = "\n\n".join(search_results_text)

    btn = []
    
    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10

    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"free_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ⏩", callback_data=f"free_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"free_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"free_{req}_{key}_{n_offset}")
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



async def free_filter(_, msg):
    message = msg
    if message.text.startswith("/"): return  # ignore commands
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return
    if 2 < len(message.text) < 100:
        search = message.text
        files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
        if not files:
            return
       
    search_results_text = []
    for file in files:
        user_id = message.from_user.id
        user_id_bytes = str(user_id).encode('utf-8')  # Convert to bytes
        urlsafe_encoded_user_id = base64.urlsafe_b64encode(user_id_bytes).decode('utf-8') 
        shortlink = await urlshare(f"https://telegram.me/{temp.U_NAME}?start={temp.U_NAME}-{urlsafe_encoded_user_id}_{file.file_id}")
        file_link = f"🎬 [{get_size(file.file_size)} | {await replace_blacklist(file.file_name, script.BLACKLIST)}]({shortlink})"
        search_results_text.append(file_link)

    search_results_text = "\n\n".join(search_results_text)

    btn = []

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="NEXT ⏩", callback_data=f"free_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    cap = f"Here is what i found for your query {search}"
    await db.update_value(message.from_user.id, "timestamps", int(time.time()))
    return f"<b>{cap}\n\n{search_results_text}</b>", InlineKeyboardMarkup(btn)


