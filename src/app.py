# streamlit_app.py

import streamlit as st
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import pyvis.network as net
from streamlit.components.v1 import html

# ---------------------------------------------
# Generate Synthetic Data
# ---------------------------------------------

def generate_synthetic_data(num_songs=100, num_artists=25):
    """
    Generate synthetic song and artist data.
    """
    np.random.seed(42) 

    # Generate artist IDs and names
    artist_ids = [f'artist_{i}' for i in range(num_artists)]
    artist_names = [f'Artist {chr(65 + i)}' for i in range(num_artists)]

    # Assign each song to a random artist
    song_artist_ids = np.random.choice(artist_ids, size=num_songs)

    # Generate synthetic song features
    song_features = {
        'song_id': [f'song_{i}' for i in range(num_songs)],
        'song_name': [f'Song {i}' for i in range(num_songs)],
        'artist_id': song_artist_ids,
        'danceability': np.random.rand(num_songs),
        'energy': np.random.rand(num_songs),
        'acousticness': np.random.rand(num_songs),
        'instrumentalness': np.random.rand(num_songs),
        'liveness': np.random.rand(num_songs),
        'valence': np.random.rand(num_songs),
    }
    songs_df = pd.DataFrame(song_features)

    artists_df = pd.DataFrame({
        'artist_id': artist_ids,
        'artist_name': artist_names
    })

    return songs_df, artists_df

# ---------------------------------------------
# Functions for Data Processing and Recommendations
# ---------------------------------------------

def aggregate_artist_profiles(songs_df, artists_df):
    """
    Aggregate features of artists' songs to create artist profiles.
    """
    features = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'valence']

    artist_profiles = songs_df.groupby('artist_id')[features].mean().reset_index()

    artist_profiles = artist_profiles.merge(artists_df, on='artist_id')

    return artist_profiles

def perform_clustering(artist_profiles):
    """
    Perform clustering on the artist profiles.
    """
    features = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'valence']
    scaler = MinMaxScaler()
    X = scaler.fit_transform(artist_profiles[features])
    kmeans = KMeans(n_clusters=5, random_state=42, n_init='auto')
    artist_profiles['cluster'] = kmeans.fit_predict(X)
    return artist_profiles

def find_top_k_artists(user_preferences, artist_profiles, k=5):
    """
    Find the top-k artists that match the user's preferences.
    """
    features = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'valence']
    user_vector = np.array([user_preferences.get(feature, 0.5) for feature in features])

    artist_profiles['similarity'] = artist_profiles[features].apply(
        lambda x: np.linalg.norm(x - user_vector), axis=1)
    top_artists = artist_profiles.nsmallest(k, 'similarity')
    return top_artists

def find_best_song(artist_id, user_preferences, songs_df):
    """
    Find the song by the artist that best matches the user's preferences.
    """
    artist_songs = songs_df[songs_df['artist_id'] == artist_id]
    features = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'valence']
    user_vector = np.array([user_preferences.get(feature, 0.5) for feature in features])

    # Compute similarity for each song
    artist_songs = artist_songs.copy()  
    artist_songs['similarity'] = artist_songs[features].apply(
        lambda x: np.linalg.norm(x - user_vector), axis=1)
    best_song = artist_songs.nsmallest(1, 'similarity').iloc[0]

    return {
        'song_name': best_song['song_name'],
        'song_id': best_song['song_id'],
        'artist_name': best_song['artist_id']
    }

# ---------------------------------------------
# Streamlit App Interface with Playlist Panel
# ---------------------------------------------

st.set_page_config(page_title='Personalized Spotify Playlist Generator', page_icon='🎵')

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {}
if 'artists_displayed' not in st.session_state:
    st.session_state.artists_displayed = False
if 'artist_selected' not in st.session_state:
    st.session_state.artist_selected = False
if 'playlist' not in st.session_state:
    st.session_state.playlist = []  # List to store selected songs
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False  

# Generate synthetic data
if 'songs_df' not in st.session_state or 'artists_df' not in st.session_state:
    songs_df, artists_df = generate_synthetic_data(num_songs=100, num_artists=25)
    st.session_state.songs_df = songs_df
    st.session_state.artists_df = artists_df
else:
    songs_df = st.session_state.songs_df
    artists_df = st.session_state.artists_df

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
        st.markdown("Use the sliders below to set how much you care about each feature:")
        features = {
            'danceability': 'Danceability',
            'energy': 'Energy',
            'acousticness': 'Acousticness',
            'instrumentalness': 'Instrumentalness',
            'liveness': 'Liveness',
            'valence': 'Positiveness (Valence)'
        }
        for feature_key, feature_name in features.items():
            st.session_state.user_preferences[feature_key] = st.slider(
                feature_name,
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.01,
                key=feature_key
            )
        # Button to submit preferences
        if st.button('Find Matching Artists'):
            st.session_state.conversation_started = True  # Set conversation as started
            st.session_state.messages.append({
                'role': 'assistant',
                'content': "Great! Based on your preferences, here are the top artists:"
            })
            st.session_state.artists_displayed = False  # Reset to display artists

# Function to write chat messages
def display_messages():
    message = st.session_state.messages[-1]
    st.chat_message(message["role"]).markdown(message['content'])

def chatbot():
    display_messages()
    # Find top artists
    artist_profiles = aggregate_artist_profiles(songs_df, artists_df)
    artist_profiles = perform_clustering(artist_profiles)
    top_artists = find_top_k_artists(st.session_state.user_preferences, artist_profiles, k=5)
    # Display top artists
    artist_list = ""
    for idx, artist in top_artists.iterrows():
        artist_list += f"- **{artist['artist_name']}** (Similarity Score: {artist['similarity']:.2f})\n"
    st.session_state.messages.append({'role': 'assistant', 'content': artist_list})
    st.session_state.artists_displayed = True
    display_messages()
    # Add message box to enter the selected artist
    st.session_state.messages.append({
        'role': 'assistant',
        'content': "Please type the name of the artist you're interested in:"
    })
    display_messages()
    # Get user input
    user_input = st.chat_input("Type the artist's name here...")
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        display_messages()
        artist_name = user_input.strip()
        artist_profiles = aggregate_artist_profiles(songs_df, artists_df)
        matching_artists = artist_profiles[artist_profiles['artist_name'].str.lower() == artist_name.lower()]
        if not matching_artists.empty:
            artist_id = matching_artists.iloc[0]['artist_id']
            best_song = find_best_song(artist_id, st.session_state.user_preferences, songs_df)
            # Add song to playlist
            st.session_state.playlist.append({
                'song_name': best_song['song_name'],
                'artist_name': artist_name
            })
            st.session_state.messages.append({
                'role': 'assistant',
                'content': f"The best matching song by **{artist_name}** is **{best_song['song_name']}**! It has been added to your playlist."
            })

            # Display the updated messages
            display_messages()

            # Prepare and display an interconnected graph of similar artists
            artist_profiles = aggregate_artist_profiles(songs_df, artists_df)
            artist_profiles = perform_clustering(artist_profiles)
            top_artists = find_top_k_artists(st.session_state.user_preferences, artist_profiles, k=5)

            # Create a graph using NetworkX
            graph = net.Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
            for idx, artist in top_artists.iterrows():
                graph.add_node(artist['artist_name'], title=f"Cluster: {artist['cluster']}, Similarity: {artist['similarity']:.2f}")
            
            for i, artist1 in enumerate(top_artists['artist_name']):
                for j, artist2 in enumerate(top_artists['artist_name']):
                    if i < j:
                        # Add edges between nodes to show connections
                        graph.add_edge(artist1, artist2)
            
            # Save and display the interactive graph
            graph.save_graph("artist_graph.html")
            with open("artist_graph.html", "r") as f:
                html_code = f.read()
            html(html_code, height=750)

            # Ask if the user wants to find another song
            st.session_state.messages.append({
                'role': 'assistant',
                'content': "Would you like to explore another artist? Adjust your preferences in the sidebar and click 'Find Matching Artists', or type 'exit' to end the session."
            })
            display_messages()

            # Reset states for next interaction
            st.session_state.artists_displayed = False
        else:
            st.session_state.messages.append({
                'role': 'assistant',
                'content': "I couldn't find that artist in the list. Please type the name exactly as shown."
            })
            display_messages()

# display the chatbot only if conversation has started
if st.session_state.conversation_started:
    chatbot()
else:
    st.write("Welcome! Adjust your music preferences using the sliders in the sidebar and click **'Find Matching Artists'** when you're ready.")
