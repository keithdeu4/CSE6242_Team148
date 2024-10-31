import time

import pandas as pd
import plotly.express as px
import pyvis.network as net
import streamlit as st
from sklearn.decomposition import PCA
from streamlit.components.v1 import html
import sqlite3

from similarity_model import find_best_song, find_top_k_artists
from graphs import display_saved_graphs

# ---------------------------------------------
# Load Data from SQLite Database
# ---------------------------------------------
def load_data():
    conn = sqlite3.connect("music_data.db")
    songs_df = pd.read_sql_query("SELECT * FROM songs", conn)
    artists_df = pd.read_sql_query("SELECT * FROM artists", conn)
    artist_profiles = pd.read_sql_query("SELECT * FROM artist_profiles", conn)
    conn.close()
    return songs_df, artists_df, artist_profiles

# ---------------------------------------------
# Chatbot Function
# ---------------------------------------------

def chatbot():
    # Header for the chat column with an icon
    st.markdown("## 💬 Chat")

    # Function to display all messages in the chat history
    def display_chat_history():
        for message in st.session_state.messages[-5:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "graph" in message:
                    html(message["graph"], height=750)

    # Display existing chat history first
    display_chat_history()

    # Get artist recommendations if this is a new search
    if st.session_state.get("need_recommendations", True):
        top_artists = find_top_k_artists(
            st.session_state.artist_profiles, st.session_state.user_preferences, k=5
        )

        # Create artist list
        artist_list = "Based on your preferences, here are the top artists:\n\n"
        for idx, artist in top_artists.iterrows():
            artist_list += f"- **{artist['artist_name']}** (Similarity Score: {artist['similarity']:.2f})\n"

        # Add prompt for user input
        artist_list += "\nPlease type the name of the artist you're interested in:"

        # Add to message history and display
        st.session_state.messages.append({"role": "assistant", "content": artist_list})
        display_chat_history()
        st.session_state.need_recommendations = False

    # Handle user input
    user_input = st.chat_input("Type the artist's name here...")
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Process the artist selection
        artist_name = user_input.strip()
        matching_artists = st.session_state.artist_profiles[
            st.session_state.artist_profiles["artist_name"].str.lower() == artist_name.lower()
        ]

        if not matching_artists.empty:
            artist_id = matching_artists.iloc[0]["artist_id"]
            best_song = find_best_song(
                songs_df, artist_id, st.session_state.user_preferences
            )

            # Add song to playlist
            st.session_state.playlist.append(
                {"song_name": best_song["song_name"], "artist_name": artist_name}
            )

            # Create the artist similarity graph
            top_artists = find_top_k_artists(
                st.session_state.artist_profiles, st.session_state.user_preferences, k=5
            )

            # Create a graph using PyVis
            graph = net.Network(
                height="750px", width="100%", bgcolor="#222222", font_color="white"
            )

            # Add nodes and edges
            for idx, artist in top_artists.iterrows():
                # Prepare detailed hover information
                hover_info = (
                    f"Name: {artist['artist_name']}\n"
                    f"Similarity: {artist['similarity']:.2f}\n"
                    f"Popularity: {artist['popularity']:.0f}\n"
                    f"Danceability: {artist['danceability']:.2f}\n"
                    f"Energy: {artist['energy']:.2f}\n"
                    f"Acousticness: {artist['acousticness']:.2f}\n"
                    f"Valence: {artist['valence']:.2f}\n"
                    f"Liveness: {artist['liveness']:.2f}"
                )

                # Add node with updated hover information
                graph.add_node(
                    artist["artist_name"],
                    title=hover_info,
                    color="#1DB954",  # Spotify green color
                )

            # Add edges between similar artists
            for i, artist1 in enumerate(top_artists["artist_name"]):
                for j, artist2 in enumerate(top_artists["artist_name"]):
                    if i < j:
                        graph.add_edge(artist1, artist2)

            # Save the graph
            graph.save_graph("artist_graph.html")

            # Read the generated HTML
            with open("artist_graph.html", "r", encoding="utf-8") as f:
                graph_html = f.read()

            # Add response and graph to message history
            response = f"The best matching song by **{artist_name}** is **{best_song['song_name']}**! It has been added to your playlist.\n\nHere's a visualization of similar artists based on your preferences:"
            st.session_state.messages.append(
                {"role": "assistant", "content": response, "graph": graph_html}
            )

            # Add follow-up message
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Would you like to explore another artist? Type another artist name, or adjust your preferences in the sidebar and click 'Find Matching Artists' for new recommendations.",
                }
            )

        else:
            # Add error message to history
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "I couldn't find that artist in the list. Please type the name exactly as shown.",
                }
            )

        # Rerun to display new messages
        st.rerun()


# ---------------------------------------------
# Main App with Tabs
# ---------------------------------------------

# Set page config
st.set_page_config(page_title="Personalized Spotify Playlist Generator", page_icon="🎵")

# Initialize session state
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

# Generate synthetic data
if "songs_df" not in st.session_state or "artists_df" not in st.session_state:
    st.session_state.songs_df, st.session_state.artists_df, st.session_state.artist_profiles = load_data()
else:
    songs_df = st.session_state.songs_df
    artists_df = st.session_state.artists_df
    artist_profiles = st.session_state.artist_profiles


# Sidebar for playlist and preferences
with st.sidebar:
    # Playlist Panel
    with st.expander("🎵 Your Playlist", expanded=True):
        if st.session_state.playlist:
            for idx, song in enumerate(st.session_state.playlist, 1):
                st.write(f"{idx}. **{song['song_name']}** by {song['artist_name']}")
        else:
            st.write("Your playlist is empty.")
        # Option to clear the playlist
        if st.button("Clear Playlist"):
            st.session_state.playlist = []
            st.rerun()

    # Preferences Panel
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

        # Capture preferences from sliders
        for feature_key, feature_name in features.items():
            st.session_state.user_preferences[feature_key] = st.slider(
                feature_name,
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.user_preferences.get(feature_key, 0.5),
                step=0.01,
                key=feature_key,
            )

        # Button to submit preferences and plot them
        if st.button("Find Matching Artists"):
            st.session_state.conversation_started = True
            st.session_state.need_recommendations = True
            st.session_state.messages = []  # Clear previous messages
            st.rerun()

# Tabs for chatbot and cluster analysis
tabs = st.tabs(["Chatbot", "Cluster Analysis", "Data Insights"])

with tabs[0]:
    # Display the chatbot
    if st.session_state.conversation_started:
        chatbot()
    else:
        st.write(
            "Welcome! Adjust your music preferences using the sliders in the sidebar and click **'Find Matching Artists'** when you're ready."
        )

with tabs[1]:
    # Cluster Analysis Tab
    st.markdown("## 🎶 Artist Preference")
    st.write("This plot shows where your preferences fall among artists:")

    # Prepare data for PCA
    preferences = st.session_state.user_preferences
    user_data = pd.DataFrame([preferences], index=["User"])
    feature_names = list(preferences.keys())

    # Aggregated artist profiles
    artist_data = st.session_state.artist_profiles[feature_names]
    artist_data["Type"] = "Artist"

    # Combine artist and user data
    combined_data = pd.concat(
        [artist_data, user_data.assign(Type="User")], ignore_index=False
    ).reset_index(drop=True)

    # Apply PCA
    pca = PCA(n_components=2)
    pca_results = pca.fit_transform(combined_data[feature_names])

    # Create a DataFrame for PCA results
    pca_df = pd.DataFrame(pca_results, columns=["PCA1", "PCA2"])
    pca_df["Type"] = combined_data["Type"].values
    pca_df["Label"] = combined_data.index

    # Plotly scatter plot for clusters
    fig = px.scatter(
        pca_df,
        x="PCA1",
        y="PCA2",
        color="Type",
        hover_name="Label",
        title="User vs. Artists Preferences",
        labels={"Label": "Entity"},
        symbol="Type",
    )

    # Display plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Data Insights Tab
with tabs[2]:
    display_saved_graphs()
