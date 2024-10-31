import sqlite3

import numpy as np
import pandas as pd


# Generate synthetic data
def generate_synthetic_data(num_songs=100, num_artists=25):
    np.random.seed(42)

    # Generate artist IDs and names
    artist_ids = [f"artist_{i}" for i in range(num_artists)]
    artist_names = [f"Artist {chr(65 + i)}" for i in range(num_artists)]

    # Define some genre options for variety
    genres = ["Pop", "Rock", "Jazz", "Hip-Hop", "Classical", "Electronic", "Country"]

    # Assign each song to a random artist and genre
    song_artist_ids = np.random.choice(artist_ids, size=num_songs)
    song_genres = np.random.choice(genres, size=num_songs)

    # Generate synthetic song features
    song_features = {
        "song_id": [f"song_{i}" for i in range(num_songs)],
        "song_name": [f"Song {i}" for i in range(num_songs)],
        "artist_id": song_artist_ids,
        "danceability": np.random.rand(num_songs),
        "energy": np.random.rand(num_songs),
        "acousticness": np.random.rand(num_songs),
        "instrumentalness": np.random.rand(num_songs),
        "liveness": np.random.rand(num_songs),
        "valence": np.random.rand(num_songs),
        "speechiness": np.random.rand(num_songs),
        "popularity": np.random.randint(0, 100, num_songs),  # Popularity scale of 0-100
        "genre": song_genres,
        "duration_ms": np.random.randint(
            180000, 300000, num_songs
        ),  # Duration between 3-5 minutes in ms
    }
    songs_df = pd.DataFrame(song_features)

    # Create artist DataFrame and merge to add artist_name to songs_df
    artists_df = pd.DataFrame({"artist_id": artist_ids, "artist_name": artist_names})
    songs_df = songs_df.merge(artists_df, on="artist_id")
    conn = sqlite3.connect("music_data.db")
    songs_df.to_sql("songs", conn, if_exists="replace", index=False)
    artists_df.to_sql("artists", conn, if_exists="replace", index=False)
    artist_profiles = aggregate_artist_profiles(songs_df, artists_df)
    artist_profiles.to_sql("artist_profiles", conn, if_exists="replace", index=False)
    conn.close()


def aggregate_artist_profiles(songs_df, artists_df):
    # Select features to aggregate
    features = [
        "danceability",
        "energy",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "speechiness",
        "popularity",
        "duration_ms",  # Include duration in artist profile
    ]

    # Aggregate by artist
    artist_profiles = songs_df.groupby("artist_id")[features].mean().reset_index()

    # Merge artist names into the aggregated profile
    artist_profiles = artist_profiles.merge(artists_df, on="artist_id")

    # Reorder columns to have artist name first for easier readability
    artist_profiles = artist_profiles[["artist_id", "artist_name"] + features]

    return artist_profiles
