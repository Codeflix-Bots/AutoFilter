from pyrogram import Client, filters , enums
from pyrogram.types import InlineKeyboardMarkup , InlineKeyboardButton
from info import ADMINS , START_IMG
import re
from database.users_chats_db import db
@Client.on_message(filters.command("post_mode") & filters.user(ADMINS))
async def update_post_mode(client, message):
    try:
        post_mode = await db.update_post_mode_handle()
        btn = [[
        InlineKeyboardButton("ᴘᴏsᴛ ᴍᴏᴅᴇ ➜", callback_data="update_post_mode"),
        InlineKeyboardButton(f"{'sɪɴɢʟᴇ' if post_mode.get('singel_post_mode', True) else 'ᴍᴜʟᴛɪ'} ᴍᴏᴅᴇ", callback_data="change_update_post_mode"),
    ],
    [
        InlineKeyboardButton("ᴜᴘʟᴏᴀᴅ ᴍᴏᴅᴇ ➜", callback_data="update_post_mode"),
        InlineKeyboardButton(f"{'ᴀʟʟ' if post_mode.get('all_files_post_mode', True) else 'ɴᴇᴡ'} ғɪʟᴇs", callback_data="all_files_post_mode"),
    ]]
        reply_markup = InlineKeyboardMarkup(btn)
        await message.reply_photo(caption="<b>sᴇʟᴇᴄᴛ ᴘᴏsᴛ ᴍᴏᴅᴇ ғʀᴏᴍ ʙᴇʟᴏᴡ :</b>", photo=START_IMG, reply_markup=reply_markup)
    except Exception as e:
        print('Err in update_post_mode', e)

@Client.on_message(filters.command("set_muc") & filters.user(ADMINS))
async def set_muc_id(client, message):
    try:
        id = message.command[1]
        if id:
            is_suc = await db.movies_update_channel_id(int(id))
            if is_suc:
                await message.reply("Successfully set movies update  channel id : " + id)
            else:
                await message.reply("Failed to set movies update channel id : " + id)
        else:
            await message.reply("Invalid channel id : " + id)
    except Exception as e:
        print('Err in set_muc_id', e)
        await message.reply("Failed to set movies channel id!")

@Client.on_message(filters.command("del_muc") & filters.user(ADMINS))
async def del_muc_id(client, message):
    try:
        is_suc = await db.del_movies_channel_id()
        if is_suc:
            await message.reply("Successfully deleted movies channel id")
        else:
            await message.reply("Failed to delete movies channel id")
    except Exception as e:
        print('Err in del_muc_id', e)
        await message.reply("Failed to delete movies channel id!")
@Client.on_message(filters.command("stream") & filters.user(ADMINS))
async def set_stream_link(client, message):
    try:
        link = message.command[1]
        if link:
            await db.set_stream_link(link)
            await message.reply("Successfully set stream link!")
        else:
            await message.reply("Usage: /stream https://t.me/bisal_files or http://t.me/bisal_files")
    except IndexError:
        await message.reply("Usage: /stream https://t.me/bisal_files or http://t.me/bisal_files")
        return


@Client.on_message(filters.command("del_stream") & filters.user(ADMINS))
async def del_stream_link(client, message):
    current_link =await db.get_stream_link()
    is_sure = await client.ask(message.chat.id, f"<b>Are you sure you want to delete this: <code>{current_link}</code> link ?\nReply with /yes or /no</b>", parse_mode=enums.ParseMode.HTML)
    if is_sure.text == "/no":
        return await message.reply("Stream link not deleted!")
    if is_sure.text == "/yes":
        if current_link:
            is_deleted = await db.del_stream_link()
            if is_deleted:
                return await message.reply(f"Successfully deleted This: {current_link} link!")
            else:
                return await message.reply("Stream link not found!\nOr something went wrong! Check logs")
        else:
            return await message.reply("Stream link not found!")
    else:
        return await message.reply("Invalid command!")
    
def checkIfLinkIsValid(link):
    if re.match(r'^https?://(?:www\.)?\S+$', link):
        return True
    else: return False
    
    
@Client.on_message(filters.command("m_grp") & filters.user(ADMINS))
async def m_grp(client, message):
    links = []
    link = await client.ask(message.chat.id ,"send me your pm search grp link or send /skiplink to skip , default is bisal_files")
    if link.text == "/skiplink":
        links.append("https://t.me/bisal_files")
    else:
        if checkIfLinkIsValid(link.text):
            links.append(link.text)
        else:
            await message.reply("Invalid link")
    link1 = await client.ask(message.chat.id ,"send me your movies grp link or send /skiplink to skip . default is bisal_files")
    if link1.text == "/skiplink":
        links.append("https://t.me/bisal_files")
    else:
        if checkIfLinkIsValid(link1.text):
            links.append(link1.text)
        else:
            await message.reply("Invalid link")
    ispm = await client.ask(message.chat.id ,"send 0 or 1")
    if ispm.text == "0" or ispm.text == "1":
        ispm = int(ispm.text)
    await message.reply(f'link1 : {links[0]}\nlink2 : {links[1]}')
    await db.get_set_grp_links(links=links , ispm=ispm)
    return await message.reply('done')
