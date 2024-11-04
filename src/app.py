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
                st.write(f"{idx}. **{song['track_name']}** by {song['artist_name']}")
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
            "danceability": "Danceability",
            "energy": "Energy",
            "acousticness": "Acousticness",
            "instrumentalness": "Instrumentalness",
            "liveness": "Liveness",
            "valence": "Positiveness (Valence)",
        }

        for feature_key, feature_name in features.items():
            st.session_state.user_preferences[feature_key] = st.slider(
                feature_name,
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.user_preferences.get(feature_key, 0.5),
                step=0.01,
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
