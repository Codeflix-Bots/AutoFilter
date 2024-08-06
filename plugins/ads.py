from pyrogram import Client, filters
from datetime import datetime, timedelta
from database.config_db import mdb
from info import ADMINS
import asyncio

@Client.on_message(filters.private & filters.command("set_ads") & filters.user(ADMINS))
async def set_ads(client, message):
    try:
        command_args = message.text.split(maxsplit=1)[1]
        if '#' not in command_args:
            await message.reply_text(f"Usage: /set_ads <ads_name>#<d:duration/i:impression_count>")
            return

        ads_name, duration_or_impression = command_args.split('#', 1)
        ads_name = ads_name.strip()

        if len(ads_name) > 35:
            await message.reply_text(f"Advertisement name should not exceed 35 characters.")
            return

        expiry_date = None
        impression_count = None

        if duration_or_impression[0] == 'd':
            # It's a duration
            duration = duration_or_impression[1:]
            if not duration.isdigit():
                await message.reply_text(f"Duration must be a number.")
                return
            expiry_date = datetime.now() + timedelta(days=int(duration))
        elif duration_or_impression[0] == 'i':
            # It's an impression count
            impression = duration_or_impression[1:]
            if not impression.isdigit():
                await message.reply_text(f"Impression count must be a number.")
                return
            impression_count = int(impression)
        else:
            await message.reply_text(f"Invalid prefix. Use 'd' for duration and 'i' for impression count.")
            return

        reply = message.reply_to_message
        if not reply:
            await message.reply_text(f"Reply to a message to set it as your advertisement.")
            return
        if not reply.text:
            await message.reply_text(f"Only text messages are supported.")
            return

        await mdb.update_advirtisment(reply.text, f"{ads_name}", expiry_date, impression_count)
        await asyncio.sleep(3)
        _, name, _ = await mdb.get_advirtisment()
        await message.reply_text(f"Advertisement: '{name}' has been set.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")


@Client.on_message(filters.private & filters.command("ads"))
async def ads(_, message):
    try:
        _, name, impression = await mdb.get_advirtisment()
        if not name:
            await message.reply_text(f"No ads set.")
            return
        if impression == 0:
            await message.reply_text(f"Advertisement: '{name}' has expired.")
            return
        await message.reply_text(f"Advertisement: '{name}' has {impression} impressions left.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@Client.on_message(filters.private & filters.command("del_ads") & filters.user(ADMINS))
async def del_ads(_, message):
    try:
        await mdb.update_advirtisment()
        await message.reply_text(f"Advertisement has been reseted.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")