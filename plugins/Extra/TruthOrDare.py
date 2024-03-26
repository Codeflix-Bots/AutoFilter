from pyrogram import filters
from pyrogram import Client
import requests 

#made by t.me/Veldxd

@Client.on_message(filters.command("test"))
async def test(_, m):
             api = requests.get("https://api.truthordarebot.xyz/v1/dare").json()
             text = m.text.split(None, 1)[1]
             bn = api["translations"]["bn"]
             de = api["translations"]["de"]
             if text.endswith("bn"):
                   await m.reply(bn)
                   return 
             if text.endswith("de"):
                   await m.reply(de)


@Client.on_message(filters.command("dare"))
async def dare(_, m):
         reply = m.reply_to_message
         if reply:
               api = requests.get("https://api.truthordarebot.xyz/v1/dare").json()
               text = api["question"]
               dare = f"""
 `{text}`
               """
               await m.reply_text(dare)
         else:
               api = requests.get("https://api.truthordarebot.xyz/v1/dare").json()
               text = api["question"]
               dare = f"""
 `{text}`
               """
               await m.reply_text(dare)

@Client.on_message(filters.command("truth"))
async def truth(_, m):
         reply = m.reply_to_message
         if reply:
               api = requests.get("https://api.truthordarebot.xyz/v1/truth").json()
               text = api["question"]
               truth = f"""
`{text}`
               """
               await m.reply_text(truth)
         else:
               api = requests.get("https://api.truthordarebot.xyz/v1/Truth").json()
               text = api["question"]
               truth = f"""
`{text}`
               """
               await m.reply_text(truth)
