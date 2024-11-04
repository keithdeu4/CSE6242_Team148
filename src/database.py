import sqlite3

import numpy as np
import pandas as pd

from queries import GET_ALL_ARTIST_PROFILES, GET_ARTIST_PROFILE, GET_SONGS_FOR_ARTIST


def get_connection():
    """Establish a SQLite database connection.

    Returns:
        sqlite3.Connection: Connection object to interact with the database.
    """
    return sqlite3.connect("assets\music_data.db")


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
