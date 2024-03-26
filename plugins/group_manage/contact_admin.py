# This is a simple code from MrTG brain 🧠.
# sending method for users, eg:- /admin hi.
# reply method for admins only, eg:- !ans 2674364 hello 
# In reply method !ans is command, {user_id} of sended person, {ur_message} your meessage for reply to use

from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT_ID
import asyncio

@Client.on_message(filters.private & filters.command("admin"))
async def forward_message_to_group(client, message):
 try:
    text = message.text.split(" ", 1)[1] 
    user_id = message.from_user.id
    name = message.from_user.mention
    await message.forward(LOG_CHANNEL)
    await client.send_message(LOG_CHANNEL, text=f"ᴀ ɴᴇᴡ ᴍᴇssᴀɢᴇ ғʀᴏᴍ {name}\n\nᴜꜱᴇʀ-ɪᴅ= <code>{user_id}</code>")
    await client.send_message(LOG_CHANNEL, text=f"ɪғ ʏᴏᴜ ᴡᴀɴɴᴀ ᴛᴏ ʀᴇᴘʟʏ ᴛʜᴇɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ\n\n<code>!ans {user_id} ur_messaage</code>")
    success_message = await message.reply_text("Mᴇssᴀɢᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴs. ᴡᴀɪᴛ ғᴏʀ ᴛʜᴇ ʀᴇᴘʟʏ.")

 except Exception as e:
    await message.reply_text(f"error{e}")

@Client.on_message(filters.command("ans", "!") & filters.user(ADMINS) & filters.chat(int(SUPPORT_CHAT_ID)))
async def reply_to_forwarded_message(client, message:Message):
 try: 
    mrtg = message.text.split(" ", 2)
    user_id = int(mrtg[1])
    reply_text = mrtg[2]
    await client.send_message(user_id, text=f"Rᴇᴘʟʏ ғʀᴏᴍ ᴍʏ ᴀᴅᴍɪɴ")
    await client.send_message(user_id, text=f"<code>{reply_text}</code>")
    await message.reply_text(f"ᴍᴇssᴀɢᴇ sᴇɴᴛ sᴜᴄᴇssғᴜʟʟʏ ᴛᴏ <a href='tg://user?id={user_id}'><b>ᴜsᴇʀ</b></a>")
 except Exception as e:
    await message.reply_text(f"error{e}")

# ɪ ᴀᴍ ɴᴏᴛ ɪɴᴛᴇʀᴇsᴛᴇᴅ ɪɴ ʙᴇɪɴɢ ʏᴏᴜʀ sᴇᴄᴏɴᴅ ғᴀᴛʜᴇʀ ... sᴏ ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴍʏ ᴄʀᴇᴅɪᴛ...

#⋗  ᴛᴇʟᴇɢʀᴀᴍ - @Codeflix_bots

#ᴛʜɪs ʟɪɴᴇ ɪs ғᴏʀ ᴄᴏᴘʏ-ᴘᴀsᴛᴇʀs...
#...ᴡʜɪʟᴇ ʏᴏᴜ ᴀʀᴇ ʀᴇᴍᴏᴠɪɴɢ ᴍʏ ᴄʀᴇᴅɪᴛ ᴀɴᴅ ᴄᴀʟʟɪɴɢ ʏᴏᴜʀsᴇʟғ ᴀ ᴅᴇᴠᴇʟᴏᴘᴇʀʀ...
 # _____ ᴊᴜsᴛ ɪᴍᴀɢɪɴᴇ, Aᴛ ᴛʜᴀᴛ ᴛɪᴍᴇ ɪ ᴀᴍ ғᴜᴄᴋɪɴɢ ʏᴏᴜʀ ᴍᴏᴍ ᴀɴᴅ sɪs ᴀᴛ sᴀᴍᴇ ᴛɪᴍᴇ, ʜᴀʀᴅᴇʀ & ᴛᴏᴏ ʜᴀʀᴅᴇʀ...

#- ᴄʀᴇᴅɪᴛ - Github - @Codeflix-bots , @erotixe
#- ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛ..
#- ᴛʜᴀɴᴋ ʏᴏᴜ ᴄᴏᴅᴇғʟɪx ʙᴏᴛs ғᴏʀ ʜᴇʟᴘɪɴɢ ᴜs ɪɴ ᴛʜɪs ᴊᴏᴜʀɴᴇʏ 
#- ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ɢɪᴠɪɴɢ ᴍᴇ ᴄʀᴇᴅɪᴛ @Codeflix-bots  
#- ғᴏʀ ᴀɴʏ ᴇʀʀᴏʀ ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ -> ᴛᴇʟᴇɢʀᴀᴍ @codeflix_bots Community @Otakflix_Network </b>
