import sqlite3

import numpy as np
import pandas as pd

from queries import GET_ALL_ARTIST_PROFILES, GET_ARTIST_PROFILE, GET_SONGS_FOR_ARTIST

from pathlib import Path

# Get the directory containing your streamlit app
BASE_DIR = Path(__file__).parent

# Construct path to assets
asset_path = BASE_DIR / "assets" / "file.csv"

def get_connection():
    """Establish a SQLite database connection.

    Returns:
        sqlite3.Connection: Connection object to interact with the database.
    """
    conn = sqlite3.connect(BASE_DIR / "assets" / "music_data.db")
    tracks_csv = BASE_DIR / "assets" / 'tracks.csv'
    albums_csv = BASE_DIR / "assets" / 'albums.csv'
    artists_csv = BASE_DIR / "assets" / 'artists.csv'
    track_artists_csv = BASE_DIR / "assets" / 'track_artists.csv'
    track_features_csv = BASE_DIR / "assets" / 'track_features.csv'
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tracks (
        track_id TEXT PRIMARY KEY,
        track_name TEXT,
        popularity INTEGER,
        duration_ms INTEGER,
        explicit BOOLEAN,
        track_external_url TEXT,
        type TEXT,
        id TEXT,
        uri TEXT,
        track_href TEXT,
        analysis_url TEXT,
        time_signature INTEGER,
        album_id TEXT
    )''')
    pd.read_csv(tracks_csv).to_sql('tracks', conn, if_exists='replace', index=False)

    # Albums Table
    cursor.execute("DROP TABLE IF EXISTS albums")
    cursor.execute('''CREATE TABLE IF NOT EXISTS albums (
        album_id TEXT PRIMARY KEY,
        album_name TEXT,
        release_date TEXT,
        album_image_url TEXT
    )''')
    pd.read_csv(albums_csv).to_sql('albums', conn, if_exists='replace', index=False)

    # Artists Table with Auto-Incrementing artist_id
    cursor.execute("DROP TABLE IF EXISTS artists")
    cursor.execute('''CREATE TABLE IF NOT EXISTS artists (
        artist_id TEXT PRIMARY KEY,
        artist_name TEXT,
        artist_popularity INTEGER,
        artist_followers INTEGER,
        artist_image_url TEXT,
        artist_external_url TEXT
    )''')
    pd.read_csv(artists_csv).to_sql('artists', conn, if_exists='replace', index=False)

    # Track_Artists Table (Many-to-Many relationship) with foreign keys
    cursor.execute("DROP TABLE IF EXISTS track_artists")
    cursor.execute('''CREATE TABLE IF NOT EXISTS track_artists (
        track_id TEXT,
        artist_id INTEGER,
        FOREIGN KEY (track_id) REFERENCES tracks (track_id),
        FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
    )''')
    pd.read_csv(track_artists_csv).to_sql('track_artists', conn, if_exists='replace', index=False)

    # Track Features Table
    cursor.execute("DROP TABLE IF EXISTS track_features")
    cursor.execute('''CREATE TABLE IF NOT EXISTS track_features (
        track_id TEXT PRIMARY KEY,
        danceability REAL,
        energy REAL,
        key INTEGER,
        loudness REAL,
        mode INTEGER,
        speechiness REAL,
        acousticness REAL,
        instrumentalness REAL,
        liveness REAL,
        valence REAL,
        tempo REAL,
        FOREIGN KEY (track_id) REFERENCES tracks (track_id)
    )''')
    pd.read_csv(track_features_csv).to_sql('track_features', conn, if_exists='replace', index=False)

    # Create Artist_profiles Table
    cursor.execute("DROP TABLE IF EXISTS artist_profiles")
    cursor.execute('''CREATE TABLE IF NOT EXISTS artist_profiles (
        artist_id INTEGER PRIMARY KEY,
        danceability REAL,
        energy REAL,
        key INTEGER,
        loudness REAL,
        mode INTEGER,
        speechiness REAL,
        acousticness REAL,
        instrumentalness REAL,
        liveness REAL,
        valence REAL,
        tempo REAL,
        FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
    )''')

    # Load artist and track feature data
    track_features_df = pd.read_csv(track_features_csv)
    track_artists_df = pd.read_csv(track_artists_csv)

    # Merge track features with artist-track mapping
    artist_features_df = track_artists_df.merge(track_features_df, on='track_id')

    # Aggregate features by artist
    artist_profiles_df = artist_features_df.groupby('artist_id').agg({
        'danceability': 'mean',
        'energy': 'mean',
        'loudness': 'mean',
        'speechiness': 'mean',
        'acousticness': 'mean',
        'instrumentalness': 'mean',
        'liveness': 'mean',
        'valence': 'mean',
        'tempo': 'mean',
    }).reset_index()

    # Insert aggregated data into the artist_profiles table
    artist_profiles_df.to_sql('artist_profiles', conn, if_exists='replace', index=False)

    # Commit changes and close the connection
    conn.commit()
    return conn

def get_artist_profile(artist_id):
    """Fetch a specific artist's profile from the database.

    Args:
        artist_id (int): The unique ID of the artist.

    Returns:
        dict or None: A dictionary with the artist's profile data, or None if not found.
    """
    conn = get_connection()
    artist_profile = pd.read_sql_query(GET_ARTIST_PROFILE, conn, params=(artist_id,))
    conn.close()

    return (
        artist_profile.to_dict(orient="records")[0]
        if not artist_profile.empty
        else None
    )


def get_artist_profiles():
    """Fetch all artist profiles from the database.

    Returns:
        pd.DataFrame or None: DataFrame containing profiles for all artists, or None if no data.
    """
    conn = get_connection()
    artist_profiles = pd.read_sql_query(GET_ALL_ARTIST_PROFILES, conn)
    conn.close()

    return artist_profiles if not artist_profiles.empty else None


def find_best_song(artist_id, user_preferences):
    """Find the song most similar to user preferences for a given artist.

    Args:
        artist_id (int): The unique ID of the artist.
        user_preferences (dict): Dictionary of user preference values for musical features.

    Returns:
        dict or None: Dictionary with the top song's name and artist name, or None if no songs are found.
    """
    conn = get_connection()
    songs_df = pd.read_sql_query(GET_SONGS_FOR_ARTIST, conn, params=(artist_id,))
    conn.close()

    if songs_df.empty:
        return None

    # Calculate Euclidean similarity with user preferences
    song_predictors = songs_df[
        [
            "danceability",
            "energy",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "loudness"
        ]
    ]
    song_distances = np.sqrt(
        ((song_predictors - pd.Series(user_preferences)) ** 2).sum(axis=1)
    )
    song_similarities = 1 / (1 + song_distances)

    songs_df["similarity"] = song_similarities

    # Sort by similarity and get the top song
    top_song = songs_df.sort_values(by="similarity", ascending=False).iloc[0]
    return {
        "artist_name": top_song["artist_name"],
        "track_name": top_song["track_name"],
        "album_image_url": top_song["album_image_url"],
        "album_name":top_song["album_name"],
        'popularity': top_song['popularity'],
        'uri': top_song['uri'],
        "track_external_url":top_song["track_external_url"]
    }


def find_top_k_artists(artist_profiles, selected_artist_profile, k=10, epsilon=1):
    """Find the top k artists similar to a given artist profile based on musical features.

    Args:
        artist_profiles (pd.DataFrame): DataFrame containing profiles of multiple artists.
        selected_artist_profile (dict or pd.Series): Profile of the selected artist for comparison.
        k (int): Number of top similar artists to return.
        epsilon (float): Small value added to distance to prevent division by zero.

    Returns:
        pd.DataFrame: DataFrame with the top k artists and their similarity scores.
    """
    if isinstance(selected_artist_profile, dict):
        selected_artist_profile = pd.Series(selected_artist_profile)

    # Select predictors and convert to a NumPy array with float64 dtype
    predictors = np.array(
        artist_profiles[
            [
                "danceability",
                "energy",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
            ]
        ],
        dtype=np.float64,
    )

    reference_values = np.array(
        selected_artist_profile[
            [
                "danceability",
                "energy",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
            ]
        ],
        dtype=np.float64,
    )

    try:
        diff = predictors - reference_values
        squared_diff = diff**2
        summed_squared_diff = np.sum(squared_diff, axis=1)
        distances = np.sqrt(summed_squared_diff)
        similarities = 1 / (epsilon + distances)
    except Exception as e:
        print("An error occurred in the similarity calculation steps:", e)
        raise

    artist_profiles = artist_profiles.copy()
    artist_profiles["similarity"] = similarities
    top_artists = artist_profiles.sort_values(by="similarity", ascending=False).head(k)

    return top_artists
