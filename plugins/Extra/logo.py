# Copyright (C) 2023 CodeFlix_Bots (telegram)
#Licensed under the  AGPL-3.0 License;
#you may not use this file except in compliance with the License.
#Author MIKEY
#if you use our codes try to donate here https://t.me/VeldXd

from pyrogram import Client, filters, idle
import pyrogram, asyncio, random, time
from pyrogram.errors import FloodWait
from pyrogram.types import *
from info import PREFIX
import requests


@Client.on_message(filters.command(["logo"], PREFIX))
async def logo(bot, msg: Message):
    if len(msg.command) == 1:
       return await msg.reply_text("Usage:\n\n /logo Ziyan")
    logo_name = msg.text.split(" ", 1)[1]
    API = f"https://api.sdbots.tech/logohq?text={logo_name}"
    req = requests.get(API).url
    await msg.reply_photo(
        photo=f"{req}")

@Client.on_message(filters.command(["animelogo"], PREFIX))
async def animelogo(bot, msg: Message):
    if len(msg.command) == 1:
       return await msg.reply_text("Usage:\n\n /animelogo Ziyan")
    logo_name = msg.text.split(" ", 1)[1]
    API = f"https://api.sdbots.tech/anime-logo?name={logo_name}"
    req = requests.get(API).url
    await msg.reply_photo(
        photo=f"{req}")
