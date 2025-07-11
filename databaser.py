import os
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth

# Spotify app credentials
SPOTIPY_CLIENT_ID = 'YOUR_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
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

# Fetch all playlists
playlists = []
results = sp.current_user_playlists()
while results:
    playlists.extend(results['items'])
    if results['next']:
        results = sp.next(results)
    else:
        break

# Data collection
rows = []

for playlist in playlists:
    playlist_name = playlist['name']
    playlist_id = playlist['id']

    # Get all tracks (paginated)
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        tracks.extend(results['items'])
        if results['next']:
            results = sp.next(results)
        else:
            break

    for item in tracks:
        track = item['track']
        added_at = item['added_at']

        if track:  # Sometimes None
            title = track['name']
            try:
                artist = ', '.join([a['name'] for a in track['artists']])
            except TypeError:
                artist = track['album']['name']
            album = track['album']['name']
            rows.append({
                'Title': title,
                'Artist': artist,
                'Album': album,
                'Date Added': added_at,
                'Playlist Name': playlist_name
            })
    print("Done with " + playlist_name)

# Create DataFrame
df = pd.DataFrame(rows)

# Save to CSV
df.to_csv('spotify_playlists.csv', index=False, encoding='utf-8')

print("CSV export complete. File saved as 'spotify_playlists.csv'.")
