import random
import time
import requests
from pyrogram import filters, Client
from pyrogram.types import Message, InputMediaPhoto
from pyrogram.errors import MediaCaptionTooLong
from pyrogram.enums import ChatAction, ParseMode

api_url_gpt = "https://nandha-api.onrender.com/ai/gpt"
api_url_bard = "https://nandha-api.onrender.com/ai/bard"

def fetch_data(api_url: str, query: str) -> tuple:
    try:
        response = requests.get(f"{api_url}/{query}")
        response.raise_for_status()
        data = response.json()
        return data.get("content", "No response from the API."), data.get("images", False)
    except requests.exceptions.RequestException as e:
        return None, f"Request error: {e}"
    except Exception as e:
        return None, f"An error occurred: {str(e)}"

@Client.on_message(filters.command(["openai", "ai", "chatgpt", "gpt", "solve"]))
async def chatgpt(_, message):
    if len(message.command) < 2:
        return await message.reply_text("**Please provide a query.**")

    query = " ".join(message.command[1:])    
    txt = await message.reply_text("**Wait patiently, requesting to API...**")
    await txt.edit("💭")
    api_response, error_message = fetch_data(api_url_gpt, query)
    await txt.edit(api_response or error_message)





@Client.on_message(filters.command(["bard", "gemini"]))
async def bard(_, message):
    chat_id = message.chat.id
    message_id = message.id
    
    if len(message.command) < 2:
        return await message.reply_text("Please provide a query.")

    query = " ".join(message.command[1:])
    txt = await message.reply_text("Wait patiently, requesting to API...")
    await txt.edit("💭")
    
    api_response, images = fetch_data(api_url_bard, query)

    medias = []
    bard = str(api_response)
    try:
       photo_url = images[-1]
    except:
        pass
    
    
    if images:
        if len(images) > 1:
            for url in images:
                medias.append(InputMediaPhoto(media=url, caption=None))
                        
            medias[-1] = InputMediaPhoto(media=photo_url, caption=bard)
            
            try:
                await Client.send_media_group(chat_id=chat_id, media=medias, reply_to_message_id=message_id)
                return await txt.delete()
            except Exception as e:
                return await txt.edit(str(e))
        elif len(images) < 2:
            image_url = images[0]
            try:
                await message.reply_photo(photo=image_url, caption=bard)
                return await txt.delete()
            except MediaCaptionTooLong:
                return await txt.edit(bard)
            except Exception as e:
                return await txt.edit(str(e))
        else:
            return await txt.edit('Somthing went wrong')
    else:
        try:
            return await txt.edit(bard)
        except Exception as e:
            return await txt.edit(str(e))


@Client.on_message(filters.command(["Lucy","ucy", "chat"],  prefixes=[".", "/", "L", "!"]))
async def chat_gpt(bot, message):
    try:
        start_time = time.time()
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        if len(message.command) < 2:
            await message.reply_text(
                "**ʜᴇʏ ʙᴀʙᴇ, ɪ ᴀᴍ ʟᴜᴄʏ ʜᴏᴡ ᴄᴀɴ ɪ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏᴅᴀʏ?**"
            )
        else:
            a = message.text.split(' ', 1)[1]
            response = requests.get(f'https://chatgpt.apinepdev.workers.dev/?question={a}')

            try:
                # Check if "results" key is present in the JSON response
                if "answer" in response.json():
                    x = response.json()["answer"]
                    end_time = time.time()
                    telegram_ping = str(round((end_time - start_time) * 1000, 3)) + " ms"
                    await message.reply_text(
                        f" {x} ",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await message.reply_text("No 'results' key found in the response.")
            except KeyError:
                # Handle any other KeyError that might occur
                await message.reply_text("Error accessing the response.")
    except Exception as e:
        await message.reply_text(f"**ʙʀᴜʜ .. ᴇʀʀᴏʀ: {e} ")
