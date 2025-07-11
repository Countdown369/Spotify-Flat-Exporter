import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime

# Replace these with your Spotify app credentials
SPOTIPY_CLIENT_ID = 'REPLACE_WITH_YOUR_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'REPLACE_WITH_YOUR_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# Define scope for accessing private playlists
SCOPE = 'playlist-read-private playlist-read-collaborative'

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
))

# Get current user ID
user_id = sp.current_user()['id']

# Get all playlists (paginated)
playlists = []
results = sp.current_user_playlists()
while results:
    playlists.extend(results['items'])
    if results['next']:
        results = sp.next(results)
    else:
        break

# Base output directory
output_dir = 'Spotify_Playlists'
os.makedirs(output_dir, exist_ok=True)

for playlist in playlists:
    playlist_name = playlist['name'].strip().replace('/', '-')
    playlist_desc = playlist.get('description', '')
    playlist_id = playlist['id']

    # Fetch all tracks (paginated)
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        tracks.extend(results['items'])
        if results['next']:
            results = sp.next(results)
        else:
            break

    # Get creation date approximation: earliest track's added_at date
    added_dates = [item['added_at'] for item in tracks if item['added_at']]
    
    if added_dates:
        earliest = min(added_dates)
        created_date_iso = datetime.datetime.fromisoformat(earliest.replace('Z', '+00:00')).strftime('%Y%m%d')
    else:
        created_date_iso = '00000000'  # fallback if no date info

    # Safe folder name: YYYYMMDD_PlaylistName
    safe_name = f"{created_date_iso}_{playlist_name}"
    playlist_folder = os.path.join(output_dir, safe_name)
    os.makedirs(playlist_folder, exist_ok=True)

    # Write track info to text file
    txt_path = os.path.join(playlist_folder, 'playlist.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Description: {playlist_desc}\n\n")
        for idx, item in enumerate(tracks):
            track = item['track']
            if track:  # Sometimes None
                name = track['name']
                # Try for song, except for podcast
                try:
                    artist = ', '.join([a['name'] for a in track['artists']])
                except TypeError:
                    artist = track['album']['name']
                album = track['album']['name']
                f.write(f"{idx + 1}. {name} - {artist} - {album}\n")

    # Download cover image
    images = playlist.get('images')
    if images:
        img_url = images[0]['url']
        img_data = requests.get(img_url).content
        img_path = os.path.join(playlist_folder, 'cover.jpg')
        with open(img_path, 'wb') as img_file:
            img_file.write(img_data)
    
    print("Done with " + playlist_name)

print("Done. All playlists have been saved.")
