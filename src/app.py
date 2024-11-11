# app.py
import time
from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pydantic import BaseModel, Field

from chatbot import Chatbot
from database import Database
from graphs import display_saved_graphs
from state_management import SessionState
from visualizations import plot_pca_visualization
from models import AudioFeature, UserPreferences, Song

class PlaylistStats(BaseModel):
    total_songs: int
    unique_artists: int
    avg_popularity: float
    feature_averages: Dict[str, float]

class PlaylistManager:
    MAX_PLAYLIST_SIZE = 50

    @staticmethod
    def filter_playlist(playlist: List[Song], search_term: str) -> List[Song]:
        if not search_term:
            return playlist
        search_term = search_term.lower()
        return [
            song for song in playlist
            if search_term in song.track_name.lower() or 
               search_term in song.artist_name.lower()
        ]

    @staticmethod
    def create_dataframe(playlist: List[Song]) -> pd.DataFrame:
        return pd.DataFrame([song.dict() for song in playlist])

    @staticmethod
    def save_to_csv(playlist: List[Song]) -> str:
        playlist_data = [
            {
                "Track": song.track_name,
                "Artist": song.artist_name,
                "Album": song.album_name,
                "Popularity": song.popularity,
                "URI": song.uri,
            }
            for song in playlist
        ]
        return pd.DataFrame(playlist_data).to_csv(index=False)

    @staticmethod
    def render_playlist_controls():
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Playlist", key="clear_btn"):
                st.session_state.playlist = []
                st.rerun()

        with col2:
            if st.button("Save Playlist", key="save_btn"):
                if st.session_state.playlist:
                    csv = PlaylistManager.save_to_csv(st.session_state.playlist)
                    st.download_button(
                        label="Download Playlist",
                        data=csv,
                        file_name="my_spotify_playlist.csv",
                        mime="text/csv",
                    )
                else:
                    st.error("No songs to save!")

    @staticmethod
    def render_playlist_item(idx: int, song: Song):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"{idx}. **[{song.track_name}]({song.track_external_url})**")
                st.caption(f"By {song.artist_name}")
                st.caption(f"Album: {song.album_name}")

                if st.button("Remove", key=f"remove_{idx}"):
                    st.session_state.playlist.remove(song)
                    st.rerun()

            with col2:
                if song.album_image_url:
                    st.image(song.album_image_url, use_column_width=True)

            st.divider()

class PlaylistAnalytics:
    @staticmethod
    @st.cache_data
    def calculate_stats(playlist_df: pd.DataFrame) -> PlaylistStats:
        audio_features = [
            "danceability", "energy", "acousticness",
            "instrumentalness", "valence", "loudness"
        ]
        
        feature_avgs = {
            feat: playlist_df[feat].mean()
            for feat in audio_features
            if feat in playlist_df
        }
        
        return PlaylistStats(
            total_songs=len(playlist_df),
            unique_artists=playlist_df["artist_name"].nunique(),
            avg_popularity=playlist_df["popularity"].mean() if "popularity" in playlist_df else 0,
            feature_averages=feature_avgs
        )

    @staticmethod
    @st.cache_data
    def create_feature_plot(feature_avgs: Dict[str, float]) -> go.Figure:
        return go.Figure([
            go.Bar(
                x=list(feature_avgs.keys()),
                y=list(feature_avgs.values()),
                marker_color="#1DB954"
            )
        ]).update_layout(
            title="Average Audio Features",
            template="plotly_dark",
            height=400
        )

class PreferencesUI:
    @staticmethod
    @st.cache_resource
    def get_feature_configs() -> Dict[str, AudioFeature]:
        return {
            "danceability": AudioFeature(
                name="Danceability",
                type="continuous",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                default=0.5,
                labels=["Less Danceable", "More Danceable"],
                description="How suitable a track is for dancing based on tempo and rhythm"
            ),
            "energy": AudioFeature(
                name="Energy",
                type="continuous",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                default=0.5,
                labels=["Calm", "Energetic"],
                description="Intensity and activity level"
            ),
            "acousticness": AudioFeature(
                name="Style",
                type="binary",
                options=["Electronic", "Acoustic"],
                description="Preference for acoustic vs electronic music"
            ),
            "instrumentalness": AudioFeature(
                name="Vocals",
                type="binary",
                options=["With Vocals", "Instrumental"],
                description="Preference for tracks with or without vocals"
            ),
            "liveness": AudioFeature(
                name="Recording Type",
                type="binary",
                options=["Studio", "Live"],
                description="Preference for studio recordings vs live performances"
            ),
            "valence": AudioFeature(
                name="Mood",
                type="continuous",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                default=0.5,
                labels=["Negative", "Positive"],
                description="Musical mood - from sad/angry to happy/cheerful"
            ),
            "loudness": AudioFeature(
                name="Loudness",
                type="continuous",
                min_value=-30.0,
                max_value=0.0,
                step=0.5,
                default=-15.0,
                labels=["Quiet", "Loud"],
                description="Overall loudness of the track"
            ),
            "popularity": AudioFeature(
                name="Popularity",
                type="continuous",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                default=50.0,
                labels=["Less Popular", "More Popular"],
                description="Artist popularity on Spotify"
            )
        }

    @classmethod
    def render_preferences_ui(cls, user_preferences: UserPreferences) -> UserPreferences:
        """Render the preferences UI and return updated preferences."""
        show_help = st.toggle("Show feature explanations", value=False)
        st.markdown("Use the controls below to set your music preferences:")

        features = cls.get_feature_configs()
        updated_values = {}

        for feature_key, feature_info in features.items():
            with st.container():
                st.write(f"**{feature_info.name}**")
                if show_help:
                    st.caption(feature_info.description)

                current_value = getattr(user_preferences, feature_key, feature_info.default)
                
                if feature_info.type == "continuous":
                    left_label, right_label = st.columns([1, 1])
                    with left_label:
                        st.caption(feature_info.labels[0])
                    with right_label:
                        st.caption(feature_info.labels[1])

                    value = st.slider(
                        "##" + feature_key,
                        min_value=float(feature_info.min_value),
                        max_value=float(feature_info.max_value),
                        value=float(current_value),
                        step=float(feature_info.step),
                        label_visibility="collapsed"
                    )
                else:  # binary
                    # Convert current value to binary index
                    current_binary = 1 if current_value > 0.5 else 0
                    value = st.radio(
                        "##" + feature_key,
                        options=[0, 1],
                        index=current_binary,
                        format_func=lambda x: feature_info.options[x],
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                    # Convert binary choice back to float value
                    value = 0.8 if value else 0.2

                updated_values[feature_key] = value
                st.divider()

        # Return updated preferences
        return UserPreferences(**updated_values)

def validate_feature_value(feature_info: AudioFeature, value: float) -> float:
    """Validate and convert feature values."""
    if feature_info.type == "continuous":
        return max(min(float(value), feature_info.max_value), feature_info.min_value)
    else:
        return 0.8 if value > 0.5 else 0.2

def handle_find_artists_button(chatbot: Chatbot):
    if st.button("Find Matching Artists"):
        with st.spinner("Finding artists that match your preferences..."):
            st.session_state.is_loading = True
            st.session_state.conversation_started = True
            st.session_state.need_recommendations = True
            st.session_state.messages = []
            time.sleep(1)
            st.session_state.is_loading = False
            st.rerun()

st.set_page_config(
    page_title="Personalized Spotify Playlist Generator",
    page_icon="🎵",
    initial_sidebar_state="expanded"
)

# Initialize components
SessionState.initialize()
database = Database()
chatbot = Chatbot(database)

# Sidebar
with st.sidebar:
    with st.expander("🎵 Your Playlist", expanded=True):
        PlaylistManager.render_playlist_controls()
        
        st.text_input(
            "Search playlist",
            key="playlist_filter",
            placeholder="Filter by song, artist, or album...",
            help="Type to filter your playlist"
        )
        
        if st.session_state.playlist:
            playlist_count = len(st.session_state.playlist)
            if playlist_count >= PlaylistManager.MAX_PLAYLIST_SIZE:
                st.warning(f"Playlist is at maximum size ({PlaylistManager.MAX_PLAYLIST_SIZE} songs)")
            else:
                st.info(f"Playlist has {playlist_count} songs (max {PlaylistManager.MAX_PLAYLIST_SIZE})")

            filtered_playlist = PlaylistManager.filter_playlist(
                st.session_state.playlist,
                st.session_state.playlist_filter
            )
            
            for idx, song in enumerate(filtered_playlist, 1):
                PlaylistManager.render_playlist_item(idx, song)
        else:
            st.write("Your playlist is empty.")

    with st.expander("🏛️ Adjust Your Music Preferences", expanded=False):
        st.session_state.user_preferences = PreferencesUI.render_preferences_ui(
            st.session_state.user_preferences
        )
        handle_find_artists_button(chatbot)

# Main content
tabs = st.tabs(["Chatbot", "Cluster Analysis", "Playlist Statistics", "Data Insights"])

with tabs[0]:
    if st.session_state.is_loading:
        st.spinner("Processing your preferences...")
    elif st.session_state.conversation_started:
        chatbot.run()
    else:
        st.write(
            "Welcome! Adjust your music preferences in the sidebar and click 'Find Matching Artists'."
        )
        with st.expander("Need help getting started?"):
            st.write("""
            1. Click '🏛️ Adjust Your Music Preferences' in the sidebar
            2. Set your preferences using the sliders and options
            3. Click 'Find Matching Artists' to start
            4. Chat with the AI to discover new music
            5. Your selected songs will appear in the playlist
            """)

with tabs[1]:
    plot_pca_visualization(
        st.session_state.artist_profiles,
        st.session_state.user_preferences
    )

with tabs[2]:
    st.markdown("### Playlist Statistics")
    if st.session_state.playlist:
        playlist_df = PlaylistManager.create_dataframe(st.session_state.playlist)
        stats = PlaylistAnalytics.calculate_stats(playlist_df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Songs", stats.total_songs)
            st.metric("Unique Artists", stats.unique_artists)
        with col2:
            st.metric("Average Popularity", f"{stats.avg_popularity:.1f}")
        
        st.markdown("#### Average Audio Features")
        if stats.feature_averages:
            fig = PlaylistAnalytics.create_feature_plot(stats.feature_averages)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add some songs to your playlist to see statistics!")

with tabs[3]:
    display_saved_graphs()