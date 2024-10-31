import numpy as np
import pandas as pd


def find_top_k_artists(artist_profiles, user_preferences: dict[str, float], k: int):
    # Extract the predictors from the data
    predictors = artist_profiles[
        [
            "danceability",
            "energy",
            "acousticness",
            "instrumentalness",
            "liveness",
            "speechiness",
            "valence",
        ]
    ]

    # Calculate Euclidean distances between each artist's feature values and the user preferences
    distances = np.sqrt(((predictors - pd.Series(user_preferences)) ** 2).sum(axis=1))
    similarities = 1 / (1 + distances)

    # Add the similarities to the original data
    data = artist_profiles.copy()
    data["similarity"] = similarities

    # Sort the data by the similarity and return the top 20 closest artists
    top_artists = data.sort_values(by="similarity", ascending=False).head(k)

    return top_artists


def find_best_song(songs_df, artist_id, user_preferences):
    # Create a dataframe filtering for just the selected artist
    artist_songs = songs_df[songs_df["artist_id"] == artist_id]

    # Select predictors from artist's songs
    song_predictors = artist_songs[
        [
            "danceability",
            "energy",
            "acousticness",
            "instrumentalness",
            "liveness",
            "speechiness",
            "valence",
        ]
    ]

    # Calculate Euclidean distances between each song's feature values and the user preferences
    song_distances = np.sqrt(
        ((song_predictors - pd.Series(user_preferences)) ** 2).sum(axis=1)
    )
    song_similarities = 1 / (1 + song_distances)

    # Add the similarities to the original data
    artist_songs = artist_songs.copy()
    artist_songs["similarity"] = song_similarities

    # Sort the artist's songs by similarity and return the top song
    top_song = artist_songs.sort_values(by="similarity", ascending=False).head(1)

    return top_song
