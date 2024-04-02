from pyrogram import Client, filters
import requests

def get_anime_info(anime_name):
    url = 'https://graphql.anilist.co'
    query = '''
    query ($anime: String) {
      Media (search: $anime, type: ANIME) {
        id
        title {
          romaji
          english
          native
        }
        description
        episodes
        status
        averageScore
        coverImage {
          large
        }
      }
    }
    '''
    variables = {'anime': anime_name}
    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()
    
    if 'errors' in data:
        error_message = data['errors'][0]['message']
        return None, f"Error retrieving anime info: {error_message}"
    
    anime_data = data['data']['Media']
    return anime_data, None

# Command handler for /anime
@Client.on_message(filters.command("anime"))
def anime_info(client, message):
    # Get the anime name from the message
    anime_name = " ".join(message.command[1:])
    # Get anime info from AniList API
    anime_info, error_message = get_anime_info(anime_name)
    # Prepare the response message
    if anime_info:
        title = anime_info['title']['romaji']
        english_title = anime_info['title']['english']
        native_title = anime_info['title']['native']
        description = anime_info['description']
        episodes = anime_info['episodes']
        status = anime_info['status']
        average_score = anime_info['averageScore']
        cover_image_url = anime_info['coverImage']['large']
        
        response = f"Title (Romaji): {title}\n"
        if english_title:
            response += f"• Title (English): {english_title}\n"
        response += f"• Episodes: {episodes}\n"
        response += f"• Status: {status}\n"
        response += f"• Average Score: {average_score}\n\n"
        response += f"Description: {description}"
        # Send photo along with text
        message.reply_photo(cover_image_url, caption=response)
    else:
        message.reply_text(error_message or "Anime not found or error retrieving information.")
