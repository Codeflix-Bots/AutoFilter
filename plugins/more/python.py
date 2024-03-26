from pyrogram import Client, filters
from pyrogram.types import Message
import traceback



@Client.on_message(filters.command("python"))
async def execute_python_code(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please enter your Python code after the command. Example: /python print('Hello, World!')")
        return

    python_code = " ".join(message.command[1:])
    
    try:
        # Execute the Python code
        exec_result = exec(python_code)
        await message.reply(f"Code executed successfully. Result: {exec_result}")
    except Exception as e:
        # Handle code execution errors
        traceback_str = traceback.format_exc()
        await message.reply(f"Code execution error: {str(e)}\nTraceback:\n{traceback_str}")
