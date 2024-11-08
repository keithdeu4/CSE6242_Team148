import time

import streamlit as st
from pyvis.network import Network

from database import find_best_song, find_top_k_artists


def display_chat_history():
    """Display the last few messages in the chat history.

    This function iterates over the last five messages in the session state,
    displaying them in the chat UI, including any graphs saved in the message content.
    """
    for message in st.session_state.messages[-5:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "graph" in message:
                st.components.v1.html(message["graph"], height=750)


def chatbot():
    """Handle chatbot interactions, providing artist recommendations and song suggestions based on user input.

    The function generates artist recommendations based on user preferences,
    handles user input for specific artist requests, finds the best matching song,
    and creates a PyVis graph of similar artists.
    """
    st.markdown("## 💬 Chat")
    display_chat_history()

    # Generate artist recommendations if this is a new search
    if st.session_state.get("need_recommendations", True):
        top_artists = find_top_k_artists(
            artist_profiles=st.session_state.artist_profiles,
            selected_artist_profile=st.session_state.user_preferences,
            k=5,
        )

        # Create and display an artist recommendation list
        artist_list = "Based on your preferences, here are the top artists:\n\n"
        top_artists = top_artists.to_dict(orient="records")
        for artist in top_artists:
            artist_list += f"- **{artist['artist_name']}** (Similarity Score: {artist['similarity']:.2f})\n"
        artist_list += "\nPlease type the name of the artist you're interested in:"

        st.session_state.messages.append({"role": "assistant", "content": artist_list})
        display_chat_history()
        st.session_state.need_recommendations = False

    # Process user input for artist selection
    user_input = st.chat_input("Type the artist's name here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        artist_name = user_input.strip()

        # Check if the entered artist exists in the artist profiles
        matching_artists = st.session_state.artist_profiles[
            st.session_state.artist_profiles["artist_name"].str.lower()
            == artist_name.lower()
        ]

        if not matching_artists.empty:
            # Retrieve artist ID and get best song recommendation
            artist_id = matching_artists.iloc[0]["artist_id"]
            best_song = find_best_song(artist_id, st.session_state.user_preferences)
            st.session_state.playlist.append(
                {
                    "track_name": best_song["track_name"],
                    "artist_name": best_song["artist_name"],
                }
            )

            # Generate a list of similar artists for the selected artist
            selected_artist_profile = matching_artists.iloc[0].to_dict()

            top_artists = find_top_k_artists(
                st.session_state.artist_profiles, selected_artist_profile, k=25
            )

            # Filter out the last ten selected artists to avoid repetition
            last_ten_artists = {
                item["artist_name"] for item in st.session_state.playlist[-10:]
            }
            filtered_artists = top_artists[
                ~top_artists["artist_name"].isin(last_ten_artists)
            ]
            top_artists = filtered_artists.head(10)

            # Create a PyVis network graph of the selected artist and similar artists
            graph = Network(
                height="750px", width="100%", bgcolor="#222222", font_color="white"
            )
            selected_artist_hover_info = (
                f"Name: {selected_artist_profile['artist_name']}\n"
                f"Popularity: {selected_artist_profile['artist_popularity']:.0f}\n"
                f"Danceability: {selected_artist_profile['danceability']:.2f}\n"
                f"Energy: {selected_artist_profile['energy']:.2f}\n"
                f"Acousticness: {selected_artist_profile['acousticness']:.2f}\n"
                f"Valence: {selected_artist_profile['valence']:.2f}\n"
                f"Liveness: {selected_artist_profile['liveness']:.2f}"
            )

            # Add central node for the selected artist
            graph.add_node(
                artist_name,
                title=selected_artist_hover_info,
                color="red",
                shape="star",
            )

            # Add nodes for each recommended artist and connect them to the selected artist node
            for _, artist in top_artists.iterrows():
                if artist["artist_name"] in last_ten_artists:
                    continue

                hover_info = (
                    f"Name: {artist['artist_name']}\n"
                    f"Similarity: {artist['similarity']:.2f}\n"
                    f"Popularity: {artist['artist_popularity']:.0f}\n"
                    f"Danceability: {artist['danceability']:.2f}\n"
                    f"Energy: {artist['energy']:.2f}\n"
                    f"Acousticness: {artist['acousticness']:.2f}\n"
                    f"Valence: {artist['valence']:.2f}\n"
                    f"Liveness: {artist['liveness']:.2f}"
                )

                graph.add_node(
                    artist["artist_name"],
                    title=hover_info,
                    color="#1DB954",
                )

                similarity_score = artist["similarity"]
                graph.add_edge(
                    artist_name,
                    artist["artist_name"],
                    value=similarity_score,
                    title=f"Similarity: {similarity_score:.2f}",
                )

            # Add connections between similar artists based on a similarity threshold
            similarity_threshold = 0.7
            for i, artist1 in top_artists.iterrows():
                for j, artist2 in top_artists.iterrows():
                    if (
                        i < j
                        and artist1["artist_name"] != artist_name
                        and artist2["artist_name"] != artist_name
                    ):
                        similarity_score = artist1["similarity"] * artist2["similarity"]
                        if similarity_score > similarity_threshold:
                            graph.add_edge(
                                artist1["artist_name"],
                                artist2["artist_name"],
                                value=similarity_score,
                                title=f"Similarity: {similarity_score:.2f}",
                            )

            # Save the generated graph as an HTML file with a unique filename
            unique_file_name = f"artist_graph_{int(time.time())}.html"
            graph.save_graph(unique_file_name)

            # Read the HTML graph to include it in the Streamlit chat UI
            with open(unique_file_name, "r", encoding="utf-8") as f:
                graph_html = f.read()

            # Add a response with the best song recommendation and visualization
            response = f"The best matching song by **{artist_name}** is **{best_song['track_name']}**! It has been added to your playlist.\n\nHere's a visualization of similar artists based on your preferences:"
            st.session_state.messages.append(
                {"role": "assistant", "content": response, "graph": graph_html}
            )

            # Prompt for further exploration
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Would you like to explore another artist? Type another artist name, or adjust your preferences in the sidebar and click 'Find Matching Artists' for new recommendations.",
                }
            )
        else:
            # If the artist is not found, provide feedback to the user
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "I couldn't find that artist in the list. Please type the name exactly as shown.",
                }
            )

        # Refresh the chat UI
        st.rerun()
