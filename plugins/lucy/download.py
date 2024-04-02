import time
from urllib.parse import urlparse
import os
import asyncio
import requests
import wget
import yt_dlp
from youtubesearchpython import SearchVideos
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import *

# ------------------------------------------------------------------------------- #
# Function to download Pinterest videos
def download_pinterest_video(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        if response.status_code == 200:
            video_url = extract_video_url(response.text)
            return video_url
        else:
            return None
    except requests.RequestException as e:
        print(f"Error downloading Pinterest video: {e}")
        return None
 
 
def extract_video_url(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        video_tag = soup.find('video')
        if video_tag:
            video_url = video_tag.get('src')
            return video_url
        else:
            return None
    except Exception as e:
        print(f"Error extracting video URL from HTML: {e}")
        return None
 
 
# ------------------------------------------------------------------------------- #
# Command to download a Pinterest video
@Client.on_message(filters.command("pinterest"))
async def download_pinterest_video_command(client, message):
    try:
        if len(message.text.split(" ")) == 1:
            await message.reply_text("Please provide a Pinterest link after the command.")
            return

        url = message.text.split(" ", 1)[1]
        video_url = download_pinterest_video(url)

        if video_url:
            await message.reply_video(video_url)
        else:
            await message.reply_text("No video found in the Pinterest link.")
    except Exception as e:
        await message.reply_text("Something went wrong, please try again later.")

# ------------------------------------------------------------------------------- #
###### INSTAGRAM REELS DOWNLOAD

@Client.on_message(filters.command("insta"))
async def download_instagram_reel(client, message):
    try:
        if len(message.text.split(" ")) == 1:
            await message.reply_text("Please provide an Instagram link after the command.")
            return
        
        url = message.text.split(" ", 1)[1]
        response = requests.post(f"https://api.qewertyy.dev/download/instagram?url={url}")
        
        if response.status_code == 200:
            data = response.json()
            if "content" in data and len(data["content"]) > 0:
                video_url = data["content"][0]["url"]
                await message.reply_video(video_url)
            else:
                await message.reply_text("No content found in the response.")
        else:
            await message.reply_text(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        await message.reply_text("Something went wrong, please try again later.")

# --------------
