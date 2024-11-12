import sqlite3
from functools import lru_cache
import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Union
from models import Song, UserPreferences
from queries import GET_ALL_ARTIST_PROFILES, GET_ARTIST_PROFILE, GET_SONGS_FOR_ARTIST
from pathlib import Path

# Get the directory containing your streamlit app
BASE_DIR = Path(__file__).parent

class Database:
    def __init__(self, db_path= BASE_DIR / "assets" / "music_data.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    @lru_cache(maxsize=1000)
    def get_artist_profile(self, artist_id: int) -> Optional[Dict]:
        """Cached artist profile retrieval."""
        with self.get_connection() as conn:
            artist_profile = pd.read_sql_query(
                GET_ARTIST_PROFILE, conn, params=(artist_id,)
            )
            return artist_profile.to_dict(orient="records")[0] if not artist_profile.empty else None

    @lru_cache(maxsize=1)
    def get_artist_profiles(self) -> Optional[pd.DataFrame]:
        """Cached retrieval of all artist profiles."""
        with self.get_connection() as conn:
            artist_profiles = pd.read_sql_query(GET_ALL_ARTIST_PROFILES, conn)
            return artist_profiles if not artist_profiles.empty else None

    def find_best_song(
        self, 
        artist_id: int, 
        user_preferences: UserPreferences
    ) -> Optional[Song]:
        """Find best matching song with proper Series handling."""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT 
                    t.track_id, t.track_name, t.popularity, t.duration_ms,
                    a.album_name, a.album_image_url,
                    ar.artist_name,
                    tf.*,
                    t.track_external_url,
                    t.uri
                FROM tracks t
                JOIN track_features tf ON t.track_id = tf.track_id
                JOIN track_artists ta ON ta.track_id = t.track_id
                JOIN artists ar ON ar.artist_id = ta.artist_id
                JOIN albums a ON t.album_id = a.album_id
                WHERE ar.artist_id = ?
                """
                songs_df = pd.read_sql_query(query, conn, params=(artist_id,))
                
                if songs_df.empty:
                    return None

                # Calculate similarity using vectorized operations
                features = [
                    "danceability", "energy", "acousticness",
                    "instrumentalness", "liveness", "valence", "loudness"
                ]
                
                song_vectors = songs_df[features].values
                pref_vector = np.array([
                    getattr(user_preferences, f) for f in features
                ])
                
                distances = np.linalg.norm(song_vectors - pref_vector, axis=1)
                similarities = 1 / (1 + distances)
                
                best_song = songs_df.iloc[similarities.argmax()]
                
                # Convert Series values to proper types
                return Song(
                    track_name=str(best_song["track_name"]),
                    artist_name=str(best_song["artist_name"]),
                    album_image_url=str(best_song["album_image_url"]),
                    album_name=str(best_song["album_name"]),
                    popularity=int(best_song["popularity"]),
                    uri=str(best_song["uri"]),
                    track_external_url=str(best_song["track_external_url"])
                )
                
        except Exception as e:
            print(f"Error finding best song: {str(e)}")
            return None

    def find_top_k_artists(
        self, 
        artist_profiles: pd.DataFrame, 
        selected_artist_profile: Union[Dict, UserPreferences], 
        k: int = 10, 
        epsilon: float = 1
    ) -> pd.DataFrame:
        """Find similar artists with better user preferences handling."""
        features = [
            "danceability", "energy", "acousticness",
            "instrumentalness", "liveness", "valence"
        ]
        
        # Handle both Dict and UserPreferences inputs
        if isinstance(selected_artist_profile, UserPreferences):
            profile_vector = np.array([
                getattr(selected_artist_profile, f) for f in features
            ])
            current_artist_name = None  # No artist to exclude for user preferences
        else:
            profile_vector = np.array([
                selected_artist_profile[f] for f in features
            ])
            current_artist_name = selected_artist_profile.get('artist_name')
        
        # Filter out current artist if it exists
        if current_artist_name:
            artist_profiles = artist_profiles[
                artist_profiles['artist_name'] != current_artist_name
            ].copy()
            
        artist_vectors = artist_profiles[features].values
        
        # Compute similarities
        differences = artist_vectors - profile_vector
        distances = np.sqrt(np.sum(differences ** 2, axis=1))
        similarities = 1 / (epsilon + distances)
        
        artist_profiles = artist_profiles.copy()
        artist_profiles["similarity"] = similarities
        return artist_profiles.nlargest(k, "similarity")