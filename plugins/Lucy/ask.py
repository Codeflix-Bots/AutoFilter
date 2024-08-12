# credits @Mrz_bots

import requests
from HorridAPI import api 
from pyrogram import Client, filters

@Client.on_message(filters.command("ask"))
async def ask(client, message):    
    if len(message.command) < 2:
        return await message.reply_text("Please provide query!")
    
    query = " ".join(message.command[1:])
    thinking_message = await message.reply_text("<b>Wait A Second..</b>")
    try:        
        response = api.llama(query)        
        await thinking_message.edit(f"Hey {message.from_user.mention},\n\nQuery: {query}\n\nResult:\n<code>{response}</code>")

    except Exception as e:  
        # print(e)
        error_message = f"Hmm, something went wrong: {str(e)}"[:100] + "...\n use /bug comment"
        await thinking_message.edit(error_message)
