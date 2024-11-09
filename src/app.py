import streamlit as st
from streamlit_sortables import sort_items
from typing import List, Dict
import time

from chatbot import chatbot
from database import get_artist_profiles
from graphs import display_saved_graphs
from state_management import initialize_session_state
from visualizations import plot_pca_visualization

MAX_PLAYLIST_SIZE = 50  # Maximum songs allowed in playlist

def initialize_enhanced_session_state():
    initialize_session_state()  # Original initialization
    if 'playlist_filter' not in st.session_state:
        st.session_state.playlist_filter = ""
    if 'is_loading' not in st.session_state:
        st.session_state.is_loading = False
    if 'show_help' not in st.session_state:
        st.session_state.show_help = False

st.set_page_config(
    page_title="Personalized Spotify Playlist Generator",
    page_icon="🎵",
    initial_sidebar_state="expanded"
)

initialize_enhanced_session_state()

def filter_playlist(playlist: List[Dict], search_term: str) -> List[Dict]:
    """Filter playlist based on search term"""
    if not search_term:
        return playlist
    search_term = search_term.lower()
    return [
        song for song in playlist
        if search_term in song['track_name'].lower() or 
           search_term in song['artist_name'].lower()
    ]

def save_playlist():
    """Save playlist to a file"""
    if not st.session_state.playlist:
        st.sidebar.error("No songs to save!")
        return
    
    # Create CSV content
    playlist_data = []
    for song in st.session_state.playlist:
        playlist_data.append({
            'Track': song['track_name'],
            'Artist': song['artist_name'],
            'URI': song.get('uri', ''),
            'Added': time.strftime('%Y-%m-%d')
        })
    
    # Convert to CSV
    import pandas as pd
    df = pd.DataFrame(playlist_data)
    csv = df.to_csv(index=False)
    
    # Create download button
    st.sidebar.download_button(
        label="Download Playlist as CSV",
        data=csv,
        file_name="my_spotify_playlist.csv",
        mime="text/csv",
    )

# Sidebar
with st.sidebar:
    with st.expander("🎵 Your Playlist", expanded=True):
        # Playlist controls in a single row
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Playlist", key="clear_btn"):
                st.session_state.playlist = []
                st.rerun()
        with col2:
            if st.button("Save Playlist", key="save_btn"):
                if not st.session_state.playlist:
                    st.error("No songs to save!")
                else:
                    # Create CSV content with available columns
                    import pandas as pd
                    playlist_data = []
                    for song in st.session_state.playlist:
                        playlist_data.append({
                            'Track': song['track_name'],
                            'Artist': song['artist_name'],
                            'Album': song['album_name'],
                            'Popularity': song['popularity'],
                            'URI': song['uri']
                        })
                    
                    df = pd.DataFrame(playlist_data)
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download Playlist",
                        data=csv,
                        file_name="my_spotify_playlist.csv",
                        mime="text/csv",
                    )
        
        # Search/filter
        st.text_input(
            "Search playlist",
            key="playlist_filter",
            placeholder="Filter by song, artist, or album...",
            help="Type to filter your playlist"
        )
        
        # Playlist display
        if st.session_state.playlist:
            playlist_count = len(st.session_state.playlist)
            MAX_PLAYLIST_SIZE = 50
            
            if playlist_count >= MAX_PLAYLIST_SIZE:
                st.warning(f"Playlist is at maximum size ({MAX_PLAYLIST_SIZE} songs)")
            else:
                st.info(f"Playlist has {playlist_count} songs (max {MAX_PLAYLIST_SIZE})")
            
            # Filter playlist
            filtered_playlist = [
                song for song in st.session_state.playlist
                if (not st.session_state.playlist_filter or 
                    st.session_state.playlist_filter.lower() in str(song['track_name']).lower() or 
                    st.session_state.playlist_filter.lower() in str(song['artist_name']).lower() or
                    st.session_state.playlist_filter.lower() in str(song.get('album_name', '')).lower())
            ]
            
            # Display filtered playlist
            for idx, song in enumerate(filtered_playlist, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Handle potential Series objects
                        track_name = song['track_name'].iloc[0] if hasattr(song['track_name'], 'iloc') else song['track_name']
                        artist_name = song['artist_name'].iloc[0] if hasattr(song['artist_name'], 'iloc') else song['artist_name']
                        album_name = song['album_name'].iloc[0] if hasattr(song['album_name'], 'iloc') else song.get('album_name', 'Unknown Album')
                        external_url = song['track_external_url'].iloc[0] if hasattr(song['track_external_url'], 'iloc') else song.get('track_external_url', '')
                        
                        # Display song information with hyperlink
                        st.write(f"{idx}. **[{track_name}]({external_url})**")
                        st.caption(f"By {artist_name}")
                        st.caption(f"Album: {album_name}")
                        
                        # Remove song button
                        if st.button("Remove", key=f"remove_{idx}"):
                            st.session_state.playlist.remove(song)
                            st.rerun()
                    
                    with col2:
                        # Check for and display album image if available
                        image_url = None
                        if 'album_image_url' in song:
                            image_url = song['album_image_url'].iloc[0] if hasattr(song['album_image_url'], 'iloc') else song['album_image_url']
                        elif 'artist_image_url' in song:
                            image_url = song['artist_image_url'].iloc[0] if hasattr(song['artist_image_url'], 'iloc') else song['artist_image_url']
                        
                        if image_url:
                            st.image(image_url, use_column_width=True)
                    
                    st.divider()
        else:
            st.write("Your playlist is empty.")
            
    with st.expander("🏛️ Adjust Your Music Preferences", expanded=False):
        # Help toggle
        show_help = st.toggle("Show feature explanations", value=False)
        
        st.markdown("Use the controls below to set your music preferences:")
        
        features = {
        "danceability": {
            "name": "Danceability",
            "type": "continuous",
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "default": 0.5,
            "labels": ["Less Danceable", "More Danceable"],
            "description": "How suitable a track is for dancing based on tempo and rhythm"
        },
        "energy": {
            "name": "Energy",
            "type": "continuous",
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "default": 0.5,
            "labels": ["Calm", "Energetic"],
            "description": "Intensity and activity level"
        },
        "acousticness": {
            "name": "Style",
            "type": "binary",
            "options": ["Electronic", "Acoustic"],
            "description": "Preference for acoustic vs electronic music"
        },
        "instrumentalness": {
            "name": "Vocals",
            "type": "binary",
            "options": ["With Vocals", "Instrumental"],
            "description": "Preference for tracks with or without vocals"
        },
        "liveness": {
            "name": "Recording Type",
            "type": "binary",
            "options": ["Studio", "Live"],
            "description": "Preference for studio recordings vs live performances"
        },
        "valence": {
            "name": "Mood",
            "type": "continuous",
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "default": 0.5,
            "labels": ["Negative", "Positive"],
            "description": "Musical mood - from sad/angry to happy/cheerful"
        },
        "loudness": {
            "name": "Loudness",
            "type": "continuous",
            "min": -30.0,
            "max": 0.0,
            "step": 0.5,
            "default": -15.0,
            "labels": ["Quiet", "Loud"],
            "description": "Overall loudness of the track"
        },
        "popularity": {
            "name": "Popularity",
            "type": "continuous",
            "min": 0,
            "max": 100,
            "step": 1,
            "default": 50,
            "labels": ["Less Popular", "More Popular"],
            "description": "Artist popularity on Spotify"
        }
    }

        # Single column layout for sidebar
        for feature_key, feature_info in features.items():
            with st.container():
                # Feature name and description
                st.write(f"**{feature_info['name']}**")
                st.caption(feature_info["description"])
                
                if feature_info["type"] == "continuous":
                    # More compact layout for continuous sliders
                    left_label, right_label = st.columns([1, 1])
                    with left_label:
                        st.caption(feature_info["labels"][0])
                    with right_label:
                        st.caption(feature_info["labels"][1])
                        
                    value = st.slider(
                        "##" + feature_key,
                        min_value=feature_info["min"],
                        max_value=feature_info["max"],
                        value=st.session_state.user_preferences.get(feature_key, feature_info["default"]),
                        step=feature_info["step"],
                        label_visibility="collapsed"
                    )
                    st.session_state.user_preferences[feature_key] = value
                        
                else:  # binary choice
                    value = st.radio(
                        "##" + feature_key,
                        options=[0, 1],
                        format_func=lambda x: feature_info["options"][x],
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                    # Convert binary choice to threshold values
                    st.session_state.user_preferences[feature_key] = 0.8 if value else 0.2
                
                # Add a small divider between controls
                st.divider()

        # Loading state for Find Matching Artists
        if st.button("Find Matching Artists"):
            with st.spinner("Finding artists that match your preferences..."):
                st.session_state.is_loading = True
                st.session_state.conversation_started = True
                st.session_state.need_recommendations = True
                st.session_state.messages = []
                time.sleep(1)  # Give visual feedback
                st.session_state.is_loading = False
                st.rerun()

# Main area tabs
tabs = st.tabs(["Chatbot", "Cluster Analysis", "Playlist Statistics","Data Insights"])

with tabs[0]:
    if st.session_state.is_loading:
        st.spinner("Processing your preferences...")
    elif st.session_state.conversation_started:
        chatbot()
    else:
        # Welcome message with help
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
        # Calculate and display various statistics about the playlist
        import pandas as pd
        import numpy as np
        
        playlist_df = pd.DataFrame(st.session_state.playlist)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Songs", len(playlist_df))
            st.metric("Unique Artists", playlist_df['artist_name'].nunique())
        
        with col2:
            avg_popularity = playlist_df['popularity'].mean() if 'popularity' in playlist_df else 0
            st.metric("Average Popularity", f"{avg_popularity:.1f}")
            
        with col3:
            if 'added_date' in playlist_df:
                st.metric("Days Growing", 
                         (pd.Timestamp.now() - playlist_df['added_date'].min()).days)
        
        # Show averages of audio features
        st.markdown("#### Average Audio Features")
        audio_features = ['danceability', 'energy', 'acousticness', 
                         'instrumentalness', 'valence', 'loudness']
        
        feature_avgs = {feat: playlist_df[feat].mean() 
                       for feat in audio_features 
                       if feat in playlist_df}
        
        # Plot average features
        if feature_avgs:
            import plotly.graph_objects as go
            
            fig = go.Figure([go.Bar(
                x=list(feature_avgs.keys()),
                y=list(feature_avgs.values()),
                marker_color='#1DB954'  # Spotify green
            )])
            
            fig.update_layout(
                title="Average Audio Features",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add some songs to your playlist to see statistics!")
        
with tabs[3]:
    display_saved_graphs()