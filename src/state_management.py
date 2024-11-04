import streamlit as st

from database import get_artist_profiles


def initialize_session_state():
    """Initialize session state variables for Streamlit.

    This function sets up default values for messages, user preferences, playlist, and artist profiles.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = {}
    if "playlist" not in st.session_state:
        st.session_state.playlist = []
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False
    if "need_recommendations" not in st.session_state:
        st.session_state.need_recommendations = True
    if "artist_profiles" not in st.session_state:
        st.session_state.artist_profiles = get_artist_profiles()
