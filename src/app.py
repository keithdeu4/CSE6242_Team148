import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import pyvis.network as net
from streamlit.components.v1 import html
import time

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
    artist_songs['similarity'] = artist_songs[features].apply(
        lambda x: np.linalg.norm(x - user_vector), axis=1)
    best_song = artist_songs.nsmallest(1, 'similarity').iloc[0]

    return {
        'song_name': best_song['song_name'],
        'song_id': best_song['song_id'],
        'artist_name': artist_songs['artist_name']
    }

# ---------------------------------------------
# Chatbot Function
# ---------------------------------------------

def chatbot():
    # Function to display all messages in the chat history
    def display_chat_history():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                # If the message has a graph, display it
                if 'graph' in message:
                    html(message['graph'], height=750)

    # Display existing chat history first
    display_chat_history()
    

    # Get artist recommendations if this is a new search
    if st.session_state.get('need_recommendations', True):
        artist_profiles = aggregate_artist_profiles(songs_df, artists_df)
        artist_profiles = perform_clustering(artist_profiles)
        top_artists = find_top_k_artists(st.session_state.user_preferences, artist_profiles, k=5)

        # Create artist list
        artist_list = "Based on your preferences, here are the top artists:\n\n"
        for idx, artist in top_artists.iterrows():
            artist_list += f"- **{artist['artist_name']}** (Similarity Score: {artist['similarity']:.2f})\n"
        
        # Add prompt for user input
        artist_list += "\nPlease type the name of the artist you're interested in:"
        
        # Add to message history and display
        st.session_state.messages.append({'role': 'assistant', 'content': artist_list})
        display_chat_history()
        st.session_state.need_recommendations = False

    # Handle user input
    user_input = st.chat_input("Type the artist's name here...")
    if user_input:
        # Add user message to history
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        
        # Process the artist selection
        artist_name = user_input.strip()
        artist_profiles = aggregate_artist_profiles(songs_df, artists_df)
        matching_artists = artist_profiles[artist_profiles['artist_name'].str.lower() == artist_name.lower()]
        
        if not matching_artists.empty:
            artist_id = matching_artists.iloc[0]['artist_id']
            best_song = find_best_song(artist_id, st.session_state.user_preferences, songs_df)

            # Add song to playlist
            st.session_state.playlist.append({
                'song_name': best_song['song_name'],
                'artist_name': best_song["artist_name"]
            })

            # Create the artist similarity graph
            artist_profiles = aggregate_artist_profiles(songs_df, artists_df)
            artist_profiles = perform_clustering(artist_profiles)
            top_artists = find_top_k_artists(st.session_state.user_preferences, artist_profiles, k=5)

            # Create a graph using PyVis
            graph = net.Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
            
            # Add nodes and edges
            for idx, artist in top_artists.iterrows():
                graph.add_node(artist['artist_name'], 
                             title=f"Cluster: {artist['cluster']}, Similarity: {artist['similarity']:.2f}",
                             color='#1DB954')  # Spotify green color
            
            # Add edges between similar artists
            for i, artist1 in enumerate(top_artists['artist_name']):
                for j, artist2 in enumerate(top_artists['artist_name']):
                    if i < j:
                        graph.add_edge(artist1, artist2)
            
            # Save the graph
            graph.save_graph("artist_graph.html")
            
            # Read the generated HTML
            with open("artist_graph.html", "r", encoding='utf-8') as f:
                graph_html = f.read()

            # Add response and graph to message history
            response = f"The best matching song by **{artist_name}** is **{best_song['song_name']}**! It has been added to your playlist.\n\nHere's a visualization of similar artists based on your preferences:"
            st.session_state.messages.append({
                'role': 'assistant', 
                'content': response,
                'graph': graph_html
            })

            # Add follow-up message
            st.session_state.messages.append({
                'role': 'assistant',
                'content': "Would you like to explore another artist? Type another artist name, or adjust your preferences in the sidebar and click 'Find Matching Artists' for new recommendations."
            })

        else:
            # Add error message to history
            st.session_state.messages.append({
                'role': 'assistant', 
                'content': "I couldn't find that artist in the list. Please type the name exactly as shown."
            })

        # Rerun to display new messages
        st.rerun()

# ---------------------------------------------
# Main App
# ---------------------------------------------

# Set page config
st.set_page_config(page_title='Personalized Spotify Playlist Generator', page_icon='🎵')

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {}
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False
if 'need_recommendations' not in st.session_state:
    st.session_state.need_recommendations = True

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
                value=st.session_state.user_preferences.get(feature_key, 0.5),
                step=0.01,
                key=feature_key
            )
        # Button to submit preferences
        if st.button('Find Matching Artists'):
            st.session_state.conversation_started = True
            st.session_state.need_recommendations = True
            st.session_state.messages = []  # Clear previous messages
            st.rerun()

# Layout columns
col1, col2 = st.columns([2, 1])

# Display the chatbot and playlist
if st.session_state.conversation_started:
    chatbot()

else:
    st.write("Welcome! Adjust your music preferences using the sliders in the sidebar and click **'Find Matching Artists'** when you're ready.")