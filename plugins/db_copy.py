from pyrogram import Client, filters
from database.ia_filterdb import get_file_details, get_all_file_ids, Media
from info import FORWARD_CHANNEL, ADMINS
import asyncio
import logging
from utils import replace_blacklist
from Script import script
from pyrogram.errors import BadRequest, FloodWait
lock = asyncio.Lock()

# Set up logging
logging.basicConfig(level=logging.ERROR)

cancel_forwarding = False


async def forward_file(client, file_id, caption):
    try:
        await client.send_cached_media(
            chat_id=FORWARD_CHANNEL,
            file_id=file_id,
            caption=caption,
        )
        return True
    except Exception as e:
        logging.error(f"Error forwarding file: {e}")
        return False


async def get_files_from_db(client, message):
    global cancel_forwarding

    m = await message.reply_text(text=f"**Be Patience, It'll Take Some Time...**")
    
    cancel_forwarding = False
    
    total_files = await Media.count_documents()
    files = await get_all_file_ids()
    total = 0
    failed = 0
    for file in files:
        if cancel_forwarding:
            await m.edit("**File forwarding process has been canceled.**")
            return

        file_id = file
        file_details = await get_file_details(file_id)
        file_info = file_details[0]
        cap = file_info.caption or file_info.file_name
        caption = f"<code>{await replace_blacklist(cap, script.BLACKLIST)}</code>"
        try:
            success = await forward_file(client, file_id, caption)
            if success:
                total += 1
                await m.edit(f"**Success** - {total}\n**Total** - {total_files}\n**Failed** - {failed}")
        except BadRequest as bad:
                failed += 1
                await m.edit(f"**Success** - {total}\n**Total** - {total_files}\n**Failed** - {failed}")
                logging.error(f"BadRequest: {bad}")
                await asyncio.sleep(1)

        except FloodWait as e:
            logging.warning(f"FloodWait: Waiting for {e.x} seconds.")
            await asyncio.sleep(e.x)

    await m.edit(f"**Successfully forwarded {total} files from the database.**")


@Client.on_message(filters.command("copydb") & filters.user(ADMINS))
async def copydb_command(client, message):
    global cancel_forwarding

    if lock.locked():
        await message.reply('Wait until previous process complete.')
    else:
        while True:
            if len(message.command) > 1:
                sub_command = message.command[1].lower()
                if sub_command == "cancel":
                    cancel_forwarding = True
                    await message.reply("**File forwarding canceled.**")
                    return
            try:
                await get_files_from_db(client, message)
                break
            except Exception as e:
                await message.reply(f"**Error: {e}**")
                break