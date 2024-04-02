import asyncio
import re
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.group_manage.database.afkdb import is_afk, add_afk, remove_afk, get_afk_users
from utils import temp

afkcheacker = 1
HANDLER = ".,?+"
BOT_USERNAME = temp.U_NAME

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

@Client.on_message(filters.command(["afk", f"afk@{BOT_USERNAME}"]) & filters.incoming)
async def going_afk(bot, message: Message):
    if message.sender_chat:
        return
    user_id = message.from_user.id
    verifier, reasondb = await is_afk(user_id)
    if verifier:
        await asyncio.sleep(1)
        await remove_afk(user_id)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time((int(time.time() - timeafk)))
            reply_text = f"**{message.from_user.first_name}** is back online and was away for {seenago}"
            if reasonafk:
                reply_text += f"\n\nReason: `{reasonafk}`"
            if afktype == "text":
                await message.reply_text(reply_text, disable_web_page_preview=True)
            elif afktype == "animation":
                await message.reply_animation(data, caption=reply_text)
            elif afktype == "photo":
                await message.reply_photo(photo=f"downloads/{user_id}.jpg", caption=reply_text)
        except Exception as e:
            print(e)
            await message.reply_text(f"**{message.from_user.first_name}** is back online", disable_web_page_preview=True)
    elif len(message.command) == 1 and not message.reply_to_message:
        details = {"type": "text", "time": time.time(), "data": None, "reason": None}
        await add_afk(user_id, details)
        await message.reply_text(f"{message.from_user.first_name} is now afk!")
    elif message.reply_to_message and (
        message.reply_to_message.animation or message.reply_to_message.photo or message.reply_to_message.sticker
    ):
        if message.reply_to_message.animation:
            _data = message.reply_to_message.animation.file_id
            _type = "animation"
        elif message.reply_to_message.photo:
            _type = "photo"
            await app.download_media(message.reply_to_message, file_name=f"{user_id}.jpg")
            _data = f"downloads/{user_id}.jpg"
        elif message.reply_to_message.sticker:
            if message.reply_to_message.sticker.is_animated:
                _type = "text"
            else:
                _type = "photo"
                await app.download_media(message.reply_to_message, file_name=f"{user_id}.jpg")
                _data = f"downloads/{user_id}.jpg"
        if len(message.command) > 1:
            _reason = (message.text.split(None, 1)[1].strip())[:100]
        else:
            _reason = None
        details = {"type": _type, "time": time.time(), "data": _data, "reason": _reason}
        await add_afk(user_id, details)
        await message.reply_text(f"{message.from_user.first_name} is now afk!")
    elif len(message.command) > 1:
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        details = {"type": "text_reason", "time": time.time(), "data": None, "reason": _reason}
        await add_afk(user_id, details)
        await message.reply_text(f"{message.from_user.first_name} is now afk!")
    else:
        await message.reply_text("Please reply to a message with an animation or photo, or provide a reason for your afk status.") 


async def chat_watcher_func(bot, message):
    if message.sender_chat:
        return
    userid = message.from_user.id
    user_name = message.from_user.first_name
    if message.entities:
        for entity in message.entities:
            if entity.type == "bot_command":
                if entity.offset == 0 and entity.length == 4:
                    text = message.text or message.caption
                    command_ = (text[0:4]).lower()
                    if command_ == "/afk":
                        return
    msg = ""
    replied_user_id = 0
    verifier, reasondb = await is_afk(userid)
    if verifier:
        await remove_afk(userid)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time((int(time.time() - timeafk)))
            if afktype == "text":
                msg += f"**{user_name[:25]}** is back online and was away for {seenago}\n\n"
            if afktype == "text_reason":
                msg += f"**{user_name[:25]}** is back online and was away for {seenago}\n\nReason: `{reasonafk}`\n\n"
            if afktype == "animation":
                if str(reasonafk) == "None":
                    await message.reply_animation(data,caption=f"**{user_name[:25]}** is back online and was away for {seenago}\n\n")
                else:
                    await message.reply_animation(data,caption=f"**{user_name[:25]}** is back online and was away for {seenago}\n\nReason: `{reasonafk}`\n\n")
            if afktype == "photo":
                if str(reasonafk) == "None":
                    await message.reply_photo(photo=f"downloads/{userid}.jpg",caption=f"**{user_name[:25]}** is back online and was away for {seenago}\n\n")
                else:
                    await message.reply_photo(photo=f"downloads/{userid}.jpg",caption=f"**{user_name[:25]}** is back online and was away for {seenago}\n\nReason: `{reasonafk}`\n\n")
        except:
            msg += f"**{user_name[:25]}** is back online\n\n"
    if message.reply_to_message:
        try:
            replied_first_name = (message.reply_to_message.from_user.first_name)
            replied_user_id = message.reply_to_message.from_user.id
            verifier, reasondb = await is_afk(replied_user_id)
            if verifier:
                try:
                    afktype = reasondb["type"]
                    timeafk = reasondb["time"]
                    data = reasondb["data"]
                    reasonafk = reasondb["reason"]
                    seenago = get_readable_time((int(time.time() - timeafk)))
                    if afktype == "text":
                        msg += f"**{replied_first_name[:25]}** is AFK since {seenago}\n\n"
                    if afktype == "text_reason":
                        msg += f"**{replied_first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n"
                    if afktype == "animation":
                        if str(reasonafk) == "None":
                            await message.reply_animation(data,caption=f"**{replied_first_name[:25]}** is AFK since {seenago}\n\n")
                        else:
                            await message.reply_animation(data,caption=f"**{replied_first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n")
                    if afktype == "photo":
                        if str(reasonafk) == "None":
                            await message.reply_photo(photo=f"downloads/{replied_user_id}.jpg",caption=f"**{replied_first_name[:25]}** is AFK since {seenago}\n\n")
                        else:
                            await message.reply_photo(photo=f"downloads/{replied_user_id}.jpg",caption=f"**{replied_first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n")
                except Exception as e:
                    print(e)
                    msg += f"**{replied_first_name}** is AFK\n\n"
        except:
            pass
    if message.entities:
        entity = message.entities
        j = 0
        for x in range(len(entity)):
            if (entity[j].type) == "mention":
                found = re.findall("@([_0-9a-zA-Z]+)", message.text)
                try:
                    get_user = found[j]
                    user = await app.get_users(get_user)
                    if user.id == replied_user_id:
                        j += 1
                        continue
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user.id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time(
                            (int(time.time() - timeafk))
                        )
                        if afktype == "text":
                            msg += f"**{user.first_name[:25]}** is AFK since {seenago}\n\n"
                        if afktype == "text_reason":
                            msg += f"**{user.first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                await message.reply_animation(data,caption=f"**{user.first_name[:25]}** is AFK since {seenago}\n\n")
                            else:
                                await message.reply_animation(data,caption=f"**{user.first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n")
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                await message.reply_photo(photo=f"downloads/{user.id}.jpg",caption=f"**{user.first_name[:25]}** is AFK since {seenago}\n\n")
                            else:
                                await message.reply_photo(photo=f"downloads/{user.id}.jpg",caption=f"**{user.first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n")
                    except:
                        msg += (f"**{user.first_name[:25]}** is AFK\n\n")
            elif (entity[j].type) == "text_mention":
                try:
                    user_id = entity[j].user.id
                    if user_id == replied_user_id:
                        j += 1
                        continue
                    first_name = entity[j].user.first_name
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user_id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time(
                            (int(time.time() - timeafk))
                        )
                        if afktype == "text":
                            msg += f"**{first_name[:25]}** is AFK since {seenago}\n\n"
                        if afktype == "text_reason":
                            msg += f"**{first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                await message.reply_animation(data,caption=f"**{first_name[:25]}** is AFK since {seenago}\n\n")
                            else:
                                await message.reply_animation(data,caption=f"**{first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n")
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                await message.reply_photo(photo=f"downloads/{user_id}.jpg",caption=f"**{first_name[:25]}** is AFK since {seenago}\n\n")
                            else:
                                await message.reply_photo(photo=f"downloads/{user_id}.jpg",caption=f"**{first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n")
                    except:
                        msg += f"**{first_name[:25]}** is AFK\n\n"
            j += 1
    if msg != "":
        try:
            return await message.reply_text(msg, disable_web_page_preview=True)
        except:
            return


#- ᴄʀᴇᴅɪᴛ - Github - @Codeflix-bots , @erotixe
#- ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛ..
#- ᴛʜᴀɴᴋ ʏᴏᴜ ᴄᴏᴅᴇғʟɪx ʙᴏᴛs ғᴏʀ ʜᴇʟᴘɪɴɢ ᴜs ɪɴ ᴛʜɪs ᴊᴏᴜʀɴᴇʏ 
#- ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ɢɪᴠɪɴɢ ᴍᴇ ᴄʀᴇᴅɪᴛ @Codeflix-bots  
#- ғᴏʀ ᴀɴʏ ᴇʀʀᴏʀ ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ -> ᴛᴇʟᴇɢʀᴀᴍ @codeflix_bots Community @Otakflix_Network </b>
