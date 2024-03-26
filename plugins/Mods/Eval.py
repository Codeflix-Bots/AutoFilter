from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import MessageTooLong
import sys, os
import re
import traceback
from io import StringIO
from info import ADMINS, EVAL_ID
import os
from pyrogram import Client, filters
import subprocess
from dotenv import load_dotenv

load_dotenv()

@Client.on_message(filters.command("install") & filters.user(ADMINS) & filters.chat(int(EVAL_ID)))
async def install_packages(client, message):
    package_names = message.text.split()[1:]

    if not package_names:
        await message.reply_text("Pʟᴇᴀsᴇ sᴘᴇᴄɪғʏ ᴘᴀᴄᴋᴀɢᴇs ᴛᴏ ɪɴsᴛᴀʟʟ (e.g:- <code>/install enchant</code>)")
        return

    try:
        subprocess.run(["pip", "install"] + package_names)
        await message.reply_text("Pᴀᴄᴋᴀɢᴇs ɪɴsᴛᴀʟʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!")
    except Exception as e:
        await message.reply_text(f"Eʀʀᴏʀ ɪɴsᴛᴀʟʟɪɴɢ ᴘᴀᴄᴋᴀɢᴇs: {e}")


@Client.on_message(filters.command("eval") & filters.chat(int(EVAL_ID)))
async def executor(client, message):
    try:
        code = message.text.split(" ", 1)[1]
    except:
        return await message.reply('Cᴏᴍᴍᴀɴᴅ Iɴᴄᴏᴍᴘʟᴇᴛᴇ!\ɴUsᴀɢᴇ: /eval python_code')
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(code, client, message)
    except:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success!"
    final_output = f"Output:\n\n<code>{evaluation}</code>"
    try:
        await message.reply(final_output)
    except MessageTooLong:
        with open('eval.txt', 'w+') as outfile:
            outfile.write(final_output)
        await message.reply_document('eval.txt')
        os.remove('eval.txt')


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)

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
