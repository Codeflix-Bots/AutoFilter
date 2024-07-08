from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import CHANNELS, MOVIE_UPDATE_CHANNEL, ADMINS
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp , formate_file_name
import re
from Script import script
from database.users_chats_db import db


processed_movies = set()
media_filter = filters.document | filters.video
@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    media = getattr(message, message.media.value, None)
    if media.mime_type in ['video/mp4', 'video/x-matroska']: 
        media.file_type = message.media.value
        media.caption = message.caption
        success_sts = await save_file(media)
        post_mode =await db.update_post_mode_handle()
        file_id, file_ref = unpack_new_file_id(media.file_id)
        if post_mode.get('all_files_post_mode', False) or success_sts == 'suc':
            await send_movie_updates(bot, file_name=media.file_name, file_id=file_id, post_mode=post_mode)

def name_format(file_name: str):
    file_name = file_name.lower()
    file_name = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name).replace('_', ' ').replace('[', '').replace(']', '')).strip()
    file_name = re.split(r's\d+|season\s*\d+|chapter\s*\d+', file_name, flags=re.IGNORECASE)[0]
    file_name = file_name.strip()
    words = file_name.split()[:4]
    imdb_file_name = ' '.join(words)
    return imdb_file_name

async def get_imdb(file_name , post_mode):
    imdb_file_name = name_format(file_name)
    imdb = await get_poster(imdb_file_name)
    file_name = f'File Name : <code>{formate_file_name(file_name)}</code>' if post_mode.get('singel_post_mode' , True) else ''
    if imdb:
        caption = script.MOVIES_UPDATE_TXT.format(
            title=imdb.get('title'),
            rating=imdb.get('rating'),
            genres=imdb.get('genres'),
            description=imdb.get('plot'),
            file_name=file_name
        )
        return imdb.get('title'), imdb.get('poster'), caption
    return None, None, None 

async def send_movie_updates(bot, file_name, file_id , post_mode):
    imdb_title, poster_url, caption = await get_imdb(file_name , post_mode)
    if not post_mode.get('singel_post_mode' , True):
        if imdb_title in processed_movies:
            return
        processed_movies.add(imdb_title)
    if not poster_url or not caption:
        return
    btn = [
        [InlineKeyboardButton('Get File', url=f'https://t.me/{temp.U_NAME}?start=pm_mode_file_{ADMINS[0]}_{file_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(btn)
    movie_update_channel =await db.movies_update_channel_id()
    try:
        await bot.send_photo(movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL, photo=poster_url, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        print('Error in send_movie_updates', e)
        pass