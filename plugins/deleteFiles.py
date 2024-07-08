import re
import logging
from pyrogram import Client, filters
from info import DELETE_CHANNELS, LOG_CHANNEL
from database.ia_filterdb import Media, unpack_new_file_id

logger = logging.getLogger(__name__)

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    media = getattr(message, message.media.value, None)
    if media.mime_type in ['video/mp4', 'video/x-matroska']: 
        file_id, _ = unpack_new_file_id(media.file_id)
        try:
            result = await Media.find_one({"file_id": file_id})
            if result:
                await result.delete()
                logger.info(f"File {media.file_name} with ID {file_id} deleted from database")
            else:
                logger.warning(f"File {media.file_name} with ID {file_id} not found in database")
        except Exception as e:
            logger.error(f"Error deleting file {media.file_name} with ID {file_id}: {str(e)}")
            await bot.send_message(LOG_CHANNEL, f"Error deleting file {media.file_name}: {str(e)}")
