import re
from pyrogram import Client, filters
from SafoneAPI import SafoneAPI

safone = SafoneAPI()




@Client.on_message(filters.command(["gen"], [".", "!", "/"]))
async def gen_cc(client, message):
    if len(message.command) < 2:
        return await message.reply_text("**ᴍᴀsᴛᴇʀ ɢɪᴠᴇ ᴍᴇ ᴘʀᴏᴠɪᴅᴇ ᴠᴀʟɪᴅ ʙɪɴ ɪ ᴡɪʟʟ ɢᴇɴᴇʀᴀᴛᴇ ᴄʀᴇᴅɪᴛ ᴄᴀʀᴅs**")

    try:
        await message.delete()
    except:
        pass

    aux = await message.reply_text("**sᴇɴsᴇɪ ᴡᴀɪᴛ \nɪ ᴡɪʟʟ ɢᴇɴᴇʀᴀᴛɪɴɢ...**")

    data = message.text.split(maxsplit=1)[1].strip()

    if not re.match(r"\d{6,}", data):
        return await aux.edit("**ᴏᴏᴘs sᴇɴsᴇɪ ᴀʀᴇ ʏᴏᴜ sᴛᴜᴘɪᴅ. ᴡʜʏ ʏᴏᴜ ɢɪᴠɪɴɢ ʙɪɴ ɪɴ ᴡʀᴏɴɢ ғᴏʀᴍᴀᴛᴇ. **")

    bin_number = data

    try:
        resp = await safone.ccgen(bin_number, 10)
        cards = resp.liveCC

        await aux.edit(f"""
**ʙɪɴ ⇾ {bin_number}**
**ᴀᴍᴏᴜɴᴛ ⇾ 10**

    
﹝⌬﹞`{cards[0]}`\n﹝⌬﹞`{cards[1]}`\n﹝⌬﹞`{cards[2]}`
﹝⌬﹞`{cards[3]}`\n﹝⌬﹞`{cards[4]}`\n﹝⌬﹞`{cards[5]}`
﹝⌬﹞`{cards[6]}`\n﹝⌬﹞`{cards[7]}`\n﹝⌬﹞`{cards[8]}`
﹝⌬﹞`{cards[9]}`
""")
    except Exception as e:
        return await aux.edit(f"**Error:** `{e}`")
