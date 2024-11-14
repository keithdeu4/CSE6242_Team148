from pathlib import Path
from typing import Dict
from pydantic import BaseModel
import streamlit as st
from database import Database

class GraphMetadata(BaseModel):
    file: str
    description: str

class GraphCategory(BaseModel):
    title: str
    graphs: Dict[str, GraphMetadata]

class GraphManager:
    def __init__(self, database: Database):
        self.database = database
        self.output_dir = Path("src/assets/graphs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_graph_categories() -> Dict[str, GraphCategory]:
        return {
            "Artist Similarity Analysis": GraphCategory(
                title="Artist Similarity Analysis",
                graphs={
                    "Similarity Network": GraphMetadata(
                        file="artist_similarity_network.html",
                        description="Interactive network showing similar artists based on musical features. Line thickness indicates similarity strength, node size shows artist popularity."
                    ),
                    "Similarity Heatmap": GraphMetadata(
                        file="similarity_heatmap.html",
                        description="Detailed similarity matrix comparing all top 25 artists. Darker colors indicate higher musical similarity."
                    ),
                    "Feature Space Clustering": GraphMetadata(
                        file="feature_space_clustering.html",
                        description="3D visualization showing how artists cluster based on danceability, energy, and valence."
                    )
                }
            ),
            "Top Artists Overview": GraphCategory(
                title="Top Artists Overview",
                graphs={
                    "Top Artists": GraphMetadata(
                        file="top_artists.html",
                        description="Rankings of top 25 artists showing both artist and average track popularity."
                    ),
                    "Success Metrics": GraphMetadata(
                        file="artist_success_metrics.html",
                        description="Scatter plot comparing artist popularity, follower count, and number of tracks."
                    ),
                    "Top Artists Radar": GraphMetadata(
                        file="top_artists_radar.html",
                        description="Radar chart comparing musical features of the top 5 artists."
                    )
                }
            ),
            "Audio Features": GraphCategory(
                title="Audio Features",
                graphs={
                    "Feature Distributions": GraphMetadata(
                        file="feature_distributions.html",
                        description="Distribution of key audio features across all tracks by top artists."
                    ),
                    "Energy-Valence Analysis": GraphMetadata(
                        file="energy_valence_quadrants.html",
                        description="Scatter plot showing how artists balance energy and emotional valence."
                    ),
                    "Artist Consistency (Danceability)": GraphMetadata(
                        file="artist_consistency_danceability.html",
                        description="How consistent each artist is in their danceability scores."
                    ),
                    "Artist Consistency (Energy)": GraphMetadata(
                        file="artist_consistency_energy.html",
                        description="How consistent each artist is in their energy levels."
                    ),
                    "Artist Consistency (Valence)": GraphMetadata(
                        file="artist_consistency_valence.html",
                        description="How consistent each artist is in their emotional tone."
                    )
                }
            ),
            "Release Patterns": GraphCategory(
                title="Release Patterns",
                graphs={
                    "Release Timeline": GraphMetadata(
                        file="release_timeline.html",
                        description="Timeline showing when each artist released tracks."
                    ),
                    "Popularity Trends": GraphMetadata(
                        file="popularity_trends.html",
                        description="How artist and track popularity have changed over time."
                    )
                }
            ),
            "Track Analysis": GraphCategory(
                title="Track Analysis",
                graphs={
                    "Duration Analysis": GraphMetadata(
                        file="duration_analysis.html",
                        description="Distribution of track lengths for each artist."
                    ),
                    "Track Popularity": GraphMetadata(
                        file="track_popularity_dist.html",
                        description="Box plot showing the distribution of track popularity scores."
                    ),
                    "Explicit Content": GraphMetadata(
                        file="explicit_content.html",
                        description="Proportion of explicit tracks in each artist's catalog."
                    )
                }
            ),
            "Success Insights": GraphCategory(
                title="Success Insights",
                graphs={
                    "Success Formula": GraphMetadata(
                        file="success_formula.html",
                        description="Table showing the common characteristics of the most popular tracks."
                    )
                }
            )
        }
        
    def verify_graphs_exist(self) -> bool:
        """Verify that all graph files exist in the output directory."""
        missing_graphs = []
        all_exist = True

        for category in self.get_graph_categories().values():
            for graph_name, metadata in category.graphs.items():
                graph_path = self.output_dir / metadata.file
                if not graph_path.exists():
                    missing_graphs.append(metadata.file)
                    all_exist = False

        if not all_exist:
            missing_list = "\n".join(missing_graphs)
            st.error(f"The following graphs are missing:\n{missing_list}")
        
        return all_exist

class GraphDisplay:
    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager
        self.categories = graph_manager.get_graph_categories()

    def display_graphs(self):
        """Display graphs with improved UI and error handling."""
        st.markdown("## 📊 Music Data Visualization")
        
        if not self.graph_manager.verify_graphs_exist():
            st.error("Some visualization files are missing. Please generate the graphs first.")
            return

        # Sidebar navigation
        st.sidebar.title("Navigation")
        category = st.sidebar.selectbox(
            "Select Analysis Category",
            options=list(self.categories.keys()),
            help="Choose a category of analysis to explore"
        )

        category_data = self.categories[category]
        
        # Main content area
        st.markdown(f"### {category_data.title}")
        
        # Graph selection
        selected_graph = st.selectbox(
            "Choose Visualization",
            options=list(category_data.graphs.keys())
        )

        graph_data = category_data.graphs[selected_graph]
        
        # Display description
        st.info(graph_data.description)

        # Display graph
        try:
            graph_path = self.graph_manager.output_dir / graph_data.file
            with open(graph_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=700)

            # Add download button
            with open(graph_path, "rb") as f:
                st.download_button(
                    label="Download Visualization",
                    data=f,
                    file_name=graph_data.file,
                    mime="text/html"
                )
        except Exception as e:
            st.error(f"Error displaying visualization: {str(e)}")

def display_saved_graphs():
    database = Database()
    graph_manager = GraphManager(database)
    graph_display = GraphDisplay(graph_manager)
    graph_display.display_graphs()
