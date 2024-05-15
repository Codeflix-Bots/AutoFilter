from pyrogram import Client, filters
from pyrogram.types import  Message
from pyrogram.types import InputMediaPhoto
from MukeshAPI import api
from pyrogram.enums import ChatAction,ParseMode

@Client.on_message(filters.command("imagine"))
async def imagine_(b, message: Message):
    if message.reply_to_message:
        text = message.reply_to_message.text
    else:

        text =message.text.split(None, 1)[1]
    Lucy=await message.reply_text( "`ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ʙʀᴏ...\n\nɢᴇɴᴇʀᴀᴛɪɴɢ ɪᴍᴀɢe...`")
    try:
        await b.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        x=api.ai_image(text)
        with open("lucy.jpg", 'wb') as f:
            f.write(x)
        caption = f"""
    ⌯ sᴜᴄᴇssғᴜʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ : {text}
    ⌯ ɢᴇɴᴇʀᴀᴛᴇᴅ ʙʏ : @lucy_filter_bot
    """
        await Lucy.delete()
        await message.reply_photo("lucy.jpg",caption=caption,quote=True)
    except Exception as e:
        await Lucy.edit_text(f"error {e}")
    

__mod_name__ = "Aɪ ɪᴍᴀɢᴇ"
__help__ = """
 ➻ /imagine : ɢᴇɴᴇʀᴀᴛᴇ Aɪ ɪᴍᴀɢᴇ ғʀᴏᴍ ᴛᴇxᴛ
 """
