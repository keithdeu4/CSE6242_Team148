import streamlit as st

from chatbot import chatbot
from database import get_artist_profiles
from state_management import initialize_session_state
from visualizations import plot_pca_visualization

st.set_page_config(page_title="Personalized Spotify Playlist Generator", page_icon="🎵")
initialize_session_state()

with st.sidebar:
    with st.expander("🎵 Your Playlist", expanded=True):
        if st.session_state.playlist:
            for idx, song in enumerate(st.session_state.playlist, 1):
                # Create two columns: one for text and one for image
                col1, col2 = st.columns([3, 1])  # Adjust column width ratios as needed
                
                with col1:
                    # Display song title and artist in the first column
                    st.write(f"{idx}. **{song['track_name']}** by {song['artist_name']}")
                
                with col2:
                    # Display song image in the second column
                    st.image(song["image"], use_column_width=True)
        else:
            st.write("Your playlist is empty.")
        if st.button("Clear Playlist"):
            st.session_state.playlist = []
            st.rerun()

    with st.expander("🏛️ Adjust Your Music Preferences", expanded=False):
        st.markdown(
            "Use the sliders below to set how much you care about each feature:"
        )
        features = {
            "danceability": {
                "name": "Danceability",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "default": 0.5
            },
            "energy": {
                "name": "Energy",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "default": 0.5
            },
            "acousticness": {
                "name": "Acousticness",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "default": 0.5
            },
            "instrumentalness": {
                "name": "Instrumentalness",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "default": 0.5
            },
            "liveness": {
                "name": "Liveness",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "default": 0.5
            },
            "valence": {
                "name": "Positiveness (Valence)",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "default": 0.5
            },
            "loudness": {
                "name": "Loudness (dB)",
                "min": -30.0,
                "max": 0.0,
                "step": 0.5,
                "default": -15.0
            },
            "popularity": {
                "name": "Popularity",
                "min": 0,
                "max": 100,
                "step": 1,
                "default": 50
            }
        }

        for feature_key, feature_info in features.items():
            st.session_state.user_preferences[feature_key] = st.slider(
                feature_info["name"],
                min_value=feature_info["min"],
                max_value=feature_info["max"],
                value=st.session_state.user_preferences.get(feature_key, feature_info["default"]),
                step=feature_info["step"],
                key=feature_key,
            )

        if st.button("Find Matching Artists"):
            st.session_state.conversation_started = True
            st.session_state.need_recommendations = True
            st.session_state.messages = []
            st.rerun()

tabs = st.tabs(["Chatbot", "Cluster Analysis", "Data Insights"])

with tabs[0]:
    if st.session_state.conversation_started:
        chatbot()
    else:
        st.write(
            "Welcome! Adjust your music preferences in the sidebar and click 'Find Matching Artists'."
        )

with tabs[1]:
    plot_pca_visualization(
        st.session_state.artist_profiles, st.session_state.user_preferences
    )
