import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from youtube_search import YoutubeSearch
import yt_dlp
import json
import random
import time

# Load API credentials from configuration file
with open('config.json') as f:
    config = json.load(f)

CLIENT_ID = config['CLIENT_ID'] #Spotify's API credentials
CLIENT_SECRET = config['CLIENT_SECRET'] #Spotify's API Credentials
REDIRECT_URI = config['REDIRECT_URI'] # Update with your redirect URI (ex. http://localhost:8888)
PLAYLIST_ID = config['PLAYLIST_ID'] # Your chosen playlist's ID (ex. 3KpLyMVUaP1vWTSqUxc2Yz)

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope='user-library-read')) 

# Get tracks from the playlist
playlist_tracks = []
try:
    results = sp.playlist_tracks(playlist_id=PLAYLIST_ID)
    while True:
        playlist_tracks.extend(results['items'])
        time.sleep(30)
        if results['next']:
            results = sp.next(results)
        else:
            break
except SpotifyException as e:
    if e.http_status == 429:
        print("Rate limit exceeded. Waiting and retrying...")
        time.sleep(60)  # Wait for a minute before retrying
        
    else:
        print("An error occurred:", e)

## Get liked songs from Spotify
## uncomment if desired

# liked_songs = []
# results = sp.current_user_saved_tracks()
# while True:
#     liked_songs.extend(results['items'])
#     if results['next']:
#         results = sp.next(results)
#     else:
#         break

# Extract artists' names and song names
extracted_data = []
for item in playlist_tracks: # extract from specific playlist with playlist_tracks or from likes with liked_songs 
    track_name = item['track']['name']
    artists_name = ', '.join(artist['name'] for artist in item['track']['artists'])
    extracted_data.append({'track_name': track_name, 'artists_name': artists_name})

# Write extracted data to a JSON file
with open('extracted_data.json', 'w') as f:
    json.dump(extracted_data, f, indent=2)

print("Liked songs data has been saved to extracted_data.json")

# Merge track_name and artists_name into a single string
merged_data = [ f"{item['track_name']} - {item['artists_name']}" for item in extracted_data]

# Shuffle the merged_data list and select first 10
random.shuffle(merged_data)
selected_tracks = merged_data[:10]

# Search YouTube for each song and get the URL
print("Starting YouTube search")
youtube_urls = []
for song in selected_tracks:
    results = YoutubeSearch(song, max_results=1).to_dict()
    if results:
        youtube_urls.append("https://www.youtube.com" + results[0]['url_suffix'])

print(youtube_urls)
print("YouTube search completed")

# Download MP3s from YouTube
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': r'C:\Users\GMC4L\Downloads\downloaded_music\Peculiar\%(title)s.%(ext)s',  # Absolute path to the output directory
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for url in youtube_urls:
        ydl.download([url])