import time
from typing import List, Dict, Optional, Set
import streamlit as st
from pyvis.network import Network
from models import Song, UserPreferences
from database import Database
import pandas as pd

class NetworkGraphBuilder:
    def __init__(self):
        self.default_image = (
            "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228"
        )

    def create_network_graph(
        self,
        selected_artist: Dict,
        similar_artists: pd.DataFrame,
        excluded_artists: Set[str]
    ) -> Network:
        """Create network graph of artist similarities."""
        graph = self._initialize_graph()
        self._add_main_artist_node(graph, selected_artist)
        self._add_similar_artist_nodes(
            graph, 
            similar_artists, 
            selected_artist["artist_name"],
            excluded_artists
        )
        self._add_connections(graph, similar_artists, selected_artist["artist_name"])
        return graph

    def _initialize_graph(self) -> Network:
        """Initialize graph with basic settings."""
        graph = Network(
            height="750px",
            width="100%",
            bgcolor="#222222",
            font_color="white"
        )
        graph.set_options(self._get_graph_options())
        return graph

    def _add_main_artist_node(self, graph: Network, artist: Dict) -> None:
        """Add main artist node to graph."""
        hover_info = self._generate_hover_info(artist)
        image_url = self._get_artist_image(artist)
        
        graph.add_node(
            artist['artist_name'],
            title=hover_info,
            label=artist['artist_name'],
            image=image_url,
            shape='circularImage',
            size=60,
            borderWidth=3,
            color="#FF4444"
        )

    def _add_similar_artist_nodes(
        self, 
        graph: Network, 
        similar_artists: pd.DataFrame,
        main_artist: str,
        excluded_artists: Set[str]
    ) -> None:
        """Add nodes for similar artists."""
        sorted_artists = similar_artists.sort_values('similarity', ascending=False)
        
        for _, artist in sorted_artists.iterrows():
            if artist["artist_name"] in excluded_artists:
                continue

            hover_info = self._generate_hover_info(
                artist, 
                include_similarity=True
            )
            image_url = self._get_artist_image(artist)

            graph.add_node(
                artist["artist_name"],
                title=hover_info,
                label=artist["artist_name"],
                image=image_url,
                shape='circularImage',
                size=50,
                borderWidth=2,
                color="#1DB954"
            )

            # Add edge with width based on similarity
            edge_width = artist["similarity"] * 2
            graph.add_edge(
                main_artist,
                artist["artist_name"],
                value=artist["similarity"],
                width=edge_width,
                title=f"Similarity: {artist['similarity']:.2f}",
            )

    def _add_connections(
        self, 
        graph: Network, 
        similar_artists: pd.DataFrame,
        main_artist: str
    ) -> None:
        """Add connections between similar artists."""
        similarity_threshold = 0.85
        max_secondary_connections = 3
        
        sorted_artists = similar_artists.sort_values('similarity', ascending=False)
        
        for i, artist1 in sorted_artists.iterrows():
            secondary_connections = 0
            for j, artist2 in sorted_artists.iterrows():
                if (
                    i < j 
                    and artist1["artist_name"] != main_artist
                    and artist2["artist_name"] != main_artist
                    and secondary_connections < max_secondary_connections
                ):
                    similarity_score = artist1["similarity"] * artist2["similarity"]
                    if similarity_score > similarity_threshold:
                        edge_width = (similarity_score - similarity_threshold) * 2
                        graph.add_edge(
                            artist1["artist_name"],
                            artist2["artist_name"],
                            value=similarity_score,
                            width=edge_width,
                            title=f"Similarity: {similarity_score:.2f}",
                        )
                        secondary_connections += 1

    def _generate_hover_info(
        self, 
        artist: Dict, 
        include_similarity: bool = False
    ) -> str:
        """Generate hover information text."""
        hover_info = [
            f"Name: {artist['artist_name']}",
            f"Popularity: {artist.get('artist_popularity', 0):.0f}"
        ]
        
        if include_similarity and 'similarity' in artist:
            hover_info.append(f"Similarity: {artist['similarity']:.2f}")
            
        features = [
            "danceability", "energy", "acousticness",
            "valence", "liveness"
        ]
        
        for feature in features:
            if feature in artist:
                hover_info.append(
                    f"{feature.title()}: {artist[feature]:.2f}"
                )
                
        return "\n".join(hover_info)

    def _get_artist_image(self, artist: Dict) -> str:
        """Get artist image URL with fallback."""
        if isinstance(artist.get('images'), list) and artist['images']:
            return artist['images'][0]['url']
        return artist.get('artist_image_url', self.default_image)

    @staticmethod
    def _get_graph_options() -> str:
        """Get graph visualization options."""
        return '''{
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -100,
                    "springLength": 250,
                    "springConstant": 0.09
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based",
                "stabilization": {
                    "enabled": true,
                    "iterations": 50
                }
            },
            "nodes": {
                "font": {
                    "size": 16,
                    "color": "white",
                    "strokeWidth": 3,
                    "strokeColor": "rgba(0, 0, 0, 0.7)"
                },
                "borderWidth": 2,
                "borderWidthSelected": 4,
                "size": 50,
                "shape": "circularImage",
                "shapeProperties": {
                    "useBorderWithImage": true,
                    "interpolation": true
                }
            },
            "edges": {
                "smooth": {
                    "type": "continuous",
                    "forceDirection": "none"
                },
                "color": {
                    "inherit": "both",
                    "opacity": 0.6
                },
                "width": 0.15
            }
        }'''

class Chatbot:
    def __init__(self, database: Database):
        self.database = database
        self.graph_builder = NetworkGraphBuilder()

    def run(self) -> None:
        """Main chatbot loop."""
        st.markdown("## 💬 Chat")
        
        # Display initial recommendations if needed
        if st.session_state.get("need_recommendations", True):
            self.show_initial_recommendations()
        
        # Always display the current chat history first
        self.display_chat_history()
        
        # Then get user input
        user_input = st.chat_input("Type the artist's name here...")
        if user_input:
            self.process_user_input(user_input)

    def display_chat_history(self):
        """Display the chat history."""
        # Create a container for messages
        with st.container():
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if "graph" in message:
                        st.components.v1.html(message["graph"], height=750)

    def process_user_input(self, user_input: str):
        """Process user input and update chat."""
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input
        })
        
        # Process the input
        artist_name = user_input.strip()
        song = self.handle_artist_selection(artist_name, st.session_state.user_preferences)

        if song:
            self.handle_successful_match(artist_name, song)
        else:
            self.handle_failed_match()
        
        # Force a rerun to update the UI
        st.rerun()

    def show_initial_recommendations(self) -> None:
        """Show initial artist recommendations based on user preferences as a graph."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        top_artists = self.database.find_top_k_artists(
            artist_profiles=st.session_state.artist_profiles,
            selected_artist_profile=st.session_state.user_preferences,
            k=5
        )

        # Create a pseudo-artist dict for the user node
        user_node = {
            "artist_name": "You",
            "artist_popularity": 100,
            "images": [],
            "artist_image_url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228"  # default image
        }
        
        # Initialize network graph
        graph = self.graph_builder._initialize_graph()
        
        # Add user node at center
        hover_info = "Your Music Profile"
        graph.add_node(
            "You",
            title=hover_info,
            label="You",
            image=user_node["artist_image_url"],
            shape='circularImage',
            size=60,
            borderWidth=3,
            color="#FF4444"
        )
        
        # Add recommended artist nodes
        top_artists_dict = top_artists.to_dict(orient="records")
        for artist in top_artists_dict:
            hover_info = self.graph_builder._generate_hover_info(
                artist,
                include_similarity=True
            )
            image_url = self.graph_builder._get_artist_image(artist)
            
            graph.add_node(
                artist["artist_name"],
                title=hover_info,
                label=artist["artist_name"],
                image=image_url,
                shape='circularImage',
                size=50,
                borderWidth=2,
                color="#1DB954"
            )
            
            # Add edge from user to artist
            edge_width = artist["similarity"] * 2
            graph.add_edge(
                "You",
                artist["artist_name"],
                value=artist["similarity"],
                width=edge_width,
                title=f"Match Score: {artist['similarity']:.2f}",
            )
        
        # Save and read the graph
        filename = f"initial_recommendations_{int(time.time())}.html"
        graph.save_graph(filename)
        with open(filename, "r", encoding="utf-8") as f:
            graph_html = f.read()

        # Add message with graph to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "Based on your preferences, here are your top artist matches! "
                "The closer an artist is to you in the center, the better the match. "
                "\n\nClick and drag to explore the visualization, and click on any artist "
                "to see more details. Type an artist's name to explore their music and "
                "find similar artists."
            ),
            "graph": graph_html
        })
        
        st.session_state.need_recommendations = False

    def handle_artist_selection(
        self, 
        artist_name: str, 
        user_preferences: UserPreferences
    ) -> Optional[Song]:
        """Handle artist selection and return best matching song."""
        matching_artists = st.session_state.artist_profiles[
            st.session_state.artist_profiles["artist_name"].str.lower() == 
            artist_name.lower()
        ]

        if matching_artists.empty:
            return None

        artist_id = matching_artists.iloc[0]["artist_id"]
        return self.database.find_best_song(artist_id, user_preferences)

    def generate_artist_graph(
        self,
        selected_artist: Dict,
        similar_artists: pd.DataFrame
    ) -> str:
        """Generate artist similarity graph."""
        last_ten_artists = {
            item.artist_name for item in st.session_state.playlist[-10:]
        }
        
        graph = self.graph_builder.create_network_graph(
            selected_artist,
            similar_artists,
            last_ten_artists
        )
        
        filename = f"artist_graph_{int(time.time())}.html"
        graph.save_graph(filename)
        
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    def handle_successful_match(self, artist_name: str, song: Song) -> None:
        """Handle successful artist match."""
        # Add song to playlist
        st.session_state.playlist.append(song)

        # Get similar artists
        matching_artists = st.session_state.artist_profiles[
            st.session_state.artist_profiles["artist_name"].str.lower() == 
            artist_name.lower()
        ]
        selected_artist = matching_artists.iloc[0].to_dict()
        
        similar_artists = self.database.find_top_k_artists(
            st.session_state.artist_profiles,
            selected_artist,
            k=10
        )

        # Generate and save graph
        graph_html = self.generate_artist_graph(selected_artist, similar_artists)

        # Add both response messages to session state
        st.session_state.messages.extend([
            {
                "role": "assistant",
                "content": (
                    f"The best matching song by **{artist_name}** is "
                    f"**{song.track_name}**! It has been added to your playlist.\n\n"
                    f"Here's a visualization of similar artists based on your preferences:"
                ),
                "graph": graph_html
            },
            {
                "role": "assistant",
                "content": (
                    "Would you like to explore another artist? Type another artist name, "
                    "or adjust your preferences in the sidebar and click 'Find Matching "
                    "Artists' for new recommendations."
                )
            }
        ])

    def handle_failed_match(self) -> None:
        """Handle case when no artist match is found."""
        st.session_state.messages.append({
            "role": "assistant",
            "content": "I couldn't find that artist in the list. Please type the name exactly as shown."
        })