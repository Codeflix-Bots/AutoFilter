from pyrogram import *
import sys
import io
import time
import os
import traceback
import pyrogram 
import requests as req
from info import *


async def aexec(code, bot, message, my, m, r, ru):
    exec(
        "async def __aexec(bot, message, my, m, r, ru): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](bot, message, my, m, r, ru)


 
def p(*args, **kwargs):
    print(*args, **kwargs)
	

@Client.on_message(filters.command('eval') & filters.user(ADMINS))
async def evaluate(bot, message):
    
    status_message = await message.reply("`Running Code...`")
    try:
        cmd = message.text.split(maxsplit=1)[1]
    except IndexError:
        await status_message.delete()
        return
    start_time = time.time()

    r = message.reply_to_message	
    m = message
    my = getattr(message, 'from_user', None)
    ru = getattr(r, 'from_user', None)

    if r:
        reply_to_id = r.id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(
		code=cmd, 
		message=message,
		my=my,
		m=message, 
		r=r,
		ru=ru,
		bot=bot
	)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    taken_time = round((time.time() - start_time), 3)
    output = evaluation.strip()
    format_text = f"Output:\n{output}"
    final_output = format_text
	
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(final_output))
        await message.reply_document(
            document=filename,
            caption=f'`{cmd}`',
            quote=True,
            
        )
        os.remove(filename)
        await status_message.delete()
        return
    else:
        await status_message.edit(final_output, parse_mode=enums.ParseMode.HTML)
        return
