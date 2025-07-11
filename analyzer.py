import pandas as pd
from datetime import datetime

# Load CSV
df = pd.read_csv('spotify_playlists.csv')

# Playlists you want to remove from analysis
playlists_to_remove = []

# Filter out that playlist
df = df[~df['Playlist Name'].isin(playlists_to_remove)]

# Group by Title + Artist and count unique playlists
song_counts = (
    df.groupby(['Title', 'Artist'])['Playlist Name']
    .nunique()
    .reset_index(name='Playlist Count')
)

# Sort descending by count
song_counts = song_counts.sort_values(by='Playlist Count', ascending=False)

# Show top N results
top_n = 20
print(f"\nTop {top_n} Songs by Playlist Appearances:\n")
print(song_counts.head(top_n).to_string(index=False))

df['Date Added'] = pd.to_datetime(df['Date Added'], errors='coerce')

# Drop rows with invalid or missing dates
df = df.dropna(subset=['Date Added'])

# Group by Title + Artist and calculate date range
spread = (
    df.groupby(['Title', 'Artist'])['Date Added']
    .agg(['min', 'max'])
    .reset_index()
)

# Calculate time delta in days
spread['Days Between Additions'] = (spread['max'] - spread['min']).dt.days

# Sort by time delta descending
spread = spread.sort_values(by='Days Between Additions', ascending=False)

# Show top N
top_n = 20
print(f"\nTop {top_n} Songs with Longest Time Between Additions:\n")
print(spread.head(top_n).to_string(index=False))
