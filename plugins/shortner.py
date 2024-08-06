import aiohttp
from database.config_db import mdb
from info import SHORTNER_SITE, SHORTNER_API

async def shortlink(link):
    shortner = await mdb.get_configuration_value("shortner")
    if shortner is None or shortner == "shareus":
        return await shareus(link)
    elif shortner == "gplinks":
        return await gplinks(link)
    if shortner == "adlinkfly":
        return await adlinkfly(link)
        
async def shareus(link):
    url = f'https://api.shareus.io/easy_api'
    api_key = "uYnR5DeLGOT72EOmEAelPA8JY622"
    params = {'key': api_key, 'link': link}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?key={api_key}&link={link}"
        return shortlink
    
async def gplinks(link):
    url = f'https://gplinks.in/api'
    api_key = "2578d98dd859758740ff88707e6a45d05213d131"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink

async def adlinkfly(link):
    #url = f"https://shortyfi.in/api"
    #api_key = "ce34a5441431b6af2d82a88cb46fd8c0301e6ff2"
    params = {'api': SHORTNER_API, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SHORTNER_SITE, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{SHORTNER_SITE}?api={SHORTNER_API}&url={link}&format=text"
        return shortlink

async def urlshare(link, linkpass=False):
    if linkpass:
        url = f"https://linkpass.onrender.com/shorten?url={link}"
    else:
        url = f'https://urlshare.onrender.com/?create&url={link}'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, raise_for_status=True) as response:
                data = await response.json()
                return data["short_url"]
    except Exception as e:
        return f"{url}"
