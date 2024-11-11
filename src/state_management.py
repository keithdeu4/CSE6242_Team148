from typing import Dict, List, Optional
import streamlit as st
from pydantic import BaseModel

from models import Song, UserPreferences
from database import Database

class SessionState:
    """Centralized session state management"""
    
    @staticmethod
    def initialize() -> None:
        """Initialize all session state variables"""
        # Core application state
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        if "user_preferences" not in st.session_state:
            st.session_state.user_preferences = UserPreferences()
            
        if "playlist" not in st.session_state:
            st.session_state.playlist = []
            
        if "conversation_started" not in st.session_state:
            st.session_state.conversation_started = False
            
        if "need_recommendations" not in st.session_state:
            st.session_state.need_recommendations = True

        # UI state
        if "playlist_filter" not in st.session_state:
            st.session_state.playlist_filter = ""
            
        if "is_loading" not in st.session_state:
            st.session_state.is_loading = False
            
        if "show_help" not in st.session_state:
            st.session_state.show_help = False

        # Data state
        if "artist_profiles" not in st.session_state:
            database = Database()
            st.session_state.artist_profiles = database.get_artist_profiles()
            
        if "graphs" not in st.session_state:
            st.session_state.graphs = {}
            
        if "callbacks_initialized" not in st.session_state:
            st.session_state.callbacks_initialized = False
            
        if "chat_container" not in st.session_state:
            st.session_state.chat_container = None
            
        if "current_graph_key" not in st.session_state:
            st.session_state.current_graph_key = None

    @staticmethod
    def reset_conversation():
        """Reset conversation-related state"""
        st.session_state.messages = []
        st.session_state.conversation_started = False
        st.session_state.need_recommendations = True

    @staticmethod
    def clear_playlist():
        """Clear playlist-related state"""
        st.session_state.playlist = []
        st.session_state.playlist_filter = ""

    @staticmethod
    def update_preferences(preferences: UserPreferences):
        """Update user preferences"""
        st.session_state.user_preferences = preferences
        st.session_state.need_recommendations = True

def initialize_session_state():
    """Initialize all session state variables"""
    SessionState.initialize()

# Default feature configurations
DEFAULT_FEATURES = {
    "danceability": 0.5,
    "energy": 0.5,
    "acousticness": 0.5,
    "instrumentalness": 0.5,
    "liveness": 0.5,
    "valence": 0.5,
    "loudness": -15.0,
    "popularity": 50
}

def get_default_preferences() -> UserPreferences:
    """Get default user preferences"""
    return UserPreferences(**DEFAULT_FEATURES)

def reset_preferences():
    """Reset preferences to defaults"""
    st.session_state.user_preferences = get_default_preferences()
    st.session_state.need_recommendations = True