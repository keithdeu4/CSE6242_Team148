import os
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
import pandas as pd
import plotly.express as px
from pydantic import BaseModel
import streamlit as st
from database import Database

class GraphMetadata(BaseModel):
    file: str
    description: str

class GraphCategory(BaseModel):
    title: str
    graphs: Dict[str, GraphMetadata]

class GraphGenerator:
    def __init__(self, database: Database):
        self.database = database
        self.output_dir = Path("assets/graphs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_graph_categories() -> Dict[str, GraphCategory]:
        return {
            "Overall Statistics": GraphCategory(
                title="Overall Statistics",
                graphs={
                    "Popularity Distribution": GraphMetadata(
                        file="popularity_distribution.html",
                        description="Distribution of artist popularity scores across the platform"
                    ),
                    "Followers by Popularity": GraphMetadata(
                        file="followers_by_popularity.html",
                        description="Relationship between artist popularity and follower count"
                    ),
                    "Feature Distributions": GraphMetadata(
                        file="feature_distributions.html",
                        description="Distribution of audio features across all artists"
                    )
                }
            ),
            "Top Artists Analysis": GraphCategory(
                title="Top Artists Analysis",
                graphs={
                    "Top Artists Features": GraphMetadata(
                        file="top_artists_features.html",
                        description="Parallel coordinates plot comparing features of top artists"
                    ),
                    "Trends Over Time": GraphMetadata(
                        file="trends_over_time.html",
                        description="Historical trends in popularity and audio features"
                    )
                }
            ),
            "Musical Characteristics": GraphCategory(
                title="Musical Characteristics",
                graphs={
                    "Time Signatures": GraphMetadata(
                        file="time_signatures.html",
                        description="Distribution of time signatures and their correlation with popularity"
                    )
                }
            )
        }

    def generate_all_graphs(self):
        """Generate all visualization graphs with improved error handling."""
        try:
            with self.database.get_connection() as conn:
                self._generate_popularity_distribution(conn)
                self._generate_follower_distribution(conn)
                self._generate_audio_features_distribution(conn)
                self._generate_top_artists_comparison(conn)
                self._generate_time_signature_distribution(conn)
                self._generate_release_year_trends(conn)
        except Exception as e:
            st.error(f"Error generating graphs: {str(e)}")
            raise

    def _generate_popularity_distribution(self, conn):
        query = """
        SELECT 
            ROUND(artist_popularity/10.0)*10 as popularity_bracket,
            COUNT(*) as count
        FROM artists
        GROUP BY ROUND(artist_popularity/10.0)*10
        ORDER BY popularity_bracket
        """
        df = pd.read_sql_query(query, conn)
        
        fig = px.bar(
            df,
            x="popularity_bracket",
            y="count",
            title="Artist Popularity Distribution",
            labels={
                "popularity_bracket": "Popularity Score (Brackets of 10)",
                "count": "Number of Artists"
            },
            template="plotly_dark"
        )
        self._save_figure(fig, "popularity_distribution.html")

    def _generate_follower_distribution(self, conn):
        query = """
        SELECT 
            ROUND(artist_popularity/10.0)*10 as popularity_bracket,
            AVG(artist_followers) as avg_followers,
            COUNT(*) as artist_count
        FROM artists
        GROUP BY ROUND(artist_popularity/10.0)*10
        ORDER BY popularity_bracket
        """
        df = pd.read_sql_query(query, conn)
        
        fig = px.scatter(
            df,
            x="popularity_bracket",
            y="avg_followers",
            size="artist_count",
            title="Average Followers by Popularity Bracket",
            labels={
                "popularity_bracket": "Popularity Score (Brackets of 10)",
                "avg_followers": "Average Follower Count",
                "artist_count": "Number of Artists"
            },
            template="plotly_dark"
        )
        fig.update_layout(yaxis_type="log")
        self._save_figure(fig, "followers_by_popularity.html")

    def _generate_audio_features_distribution(self, conn):
        query = """
        WITH ArtistAverages AS (
            SELECT 
                ar.artist_id,
                AVG(tf.danceability) as avg_danceability,
                AVG(tf.energy) as avg_energy,
                AVG(tf.acousticness) as avg_acousticness,
                AVG(tf.valence) as avg_valence
            FROM artists ar
            JOIN track_artists ta ON ar.artist_id = ta.artist_id
            JOIN track_features tf ON ta.track_id = tf.track_id
            GROUP BY ar.artist_id
        )
        SELECT 
            'Danceability' as feature, avg_danceability as value FROM ArtistAverages
        UNION ALL
        SELECT 'Energy' as feature, avg_energy as value FROM ArtistAverages
        UNION ALL
        SELECT 'Acousticness' as feature, avg_acousticness as value FROM ArtistAverages
        UNION ALL
        SELECT 'Valence' as feature, avg_valence as value FROM ArtistAverages
        """
        df = pd.read_sql_query(query, conn)
        
        fig = px.violin(
            df,
            x="feature",
            y="value",
            title="Distribution of Audio Features Across All Artists",
            box=True,
            template="plotly_dark"
        )
        self._save_figure(fig, "feature_distributions.html")

    def _save_figure(self, fig, filename: str):
        """Save plotly figure with error handling."""
        try:
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
        except Exception as e:
            st.error(f"Error saving figure {filename}: {str(e)}")
            raise

    def _generate_top_artists_comparison(self, conn):
        """Generate parallel coordinates plot comparing features of top artists."""
        query = """
        WITH TopArtists AS (
            SELECT 
                ar.artist_id,
                ar.artist_name,
                ar.artist_popularity,
                AVG(tf.danceability) as avg_danceability,
                AVG(tf.energy) as avg_energy,
                AVG(tf.acousticness) as avg_acousticness,
                AVG(tf.instrumentalness) as avg_instrumentalness,
                AVG(tf.valence) as avg_valence,
                AVG(tf.tempo) as avg_tempo
            FROM artists ar
            JOIN track_artists ta ON ar.artist_id = ta.artist_id
            JOIN track_features tf ON ta.track_id = tf.track_id
            WHERE ar.artist_popularity >= 80
            GROUP BY ar.artist_id, ar.artist_name, ar.artist_popularity
            ORDER BY ar.artist_popularity DESC
            LIMIT 50
        )
        SELECT *
        FROM TopArtists
        """
        df = pd.read_sql_query(query, conn)
        
        # Normalize numeric columns for parallel coordinates
        columns_to_normalize = ['avg_danceability', 'avg_energy', 'avg_acousticness',
                            'avg_instrumentalness', 'avg_valence', 'avg_tempo']
        
        for col in columns_to_normalize:
            if col == 'avg_tempo':
                # Special handling for tempo to bring it to 0-1 scale
                df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            # Other features are already 0-1 scaled

        fig = px.parallel_coordinates(
            df,
            dimensions=['artist_popularity'] + columns_to_normalize,
            title="Top 50 Artists - Feature Comparison",
            labels={
                'artist_popularity': 'Popularity',
                'avg_danceability': 'Danceability',
                'avg_energy': 'Energy',
                'avg_acousticness': 'Acousticness',
                'avg_instrumentalness': 'Instrumentalness',
                'avg_valence': 'Valence',
                'avg_tempo': 'Tempo (Normalized)'
            },
            color='artist_popularity',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        
        fig.update_layout(template="plotly_dark")
        self._save_figure(fig, "top_artists_features.html")

    def _generate_release_year_trends(self, conn):
        """Generate visualization of trends over time in popularity and audio features."""
        query = """
        WITH YearlyAverages AS (
            SELECT 
                CAST(strftime('%Y', t.release_date) AS INTEGER) as release_year,
                AVG(ar.artist_popularity) as avg_popularity,
                AVG(tf.danceability) as avg_danceability,
                AVG(tf.energy) as avg_energy,
                AVG(tf.acousticness) as avg_acousticness,
                AVG(tf.valence) as avg_valence
            FROM tracks t
            JOIN track_artists ta ON t.track_id = ta.track_id
            JOIN artists ar ON ta.artist_id = ar.artist_id
            JOIN track_features tf ON t.track_id = tf.track_id
            WHERE release_year >= 1990 
            AND release_year <= strftime('%Y', 'now')
            GROUP BY release_year
            ORDER BY release_year
        )
        SELECT *
        FROM YearlyAverages
        """
        df = pd.read_sql_query(query, conn)
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add popularity line on primary y-axis
        fig.add_trace(
            go.Scatter(
                x=df['release_year'],
                y=df['avg_popularity'],
                name="Popularity",
                line=dict(color="yellow", width=2)
            ),
            secondary_y=False
        )
        
        # Add audio features on secondary y-axis
        features = {
            'avg_danceability': 'Danceability',
            'avg_energy': 'Energy',
            'avg_acousticness': 'Acousticness',
            'avg_valence': 'Valence'
        }
        
        colors = px.colors.qualitative.Set3
        for i, (column, name) in enumerate(features.items()):
            fig.add_trace(
                go.Scatter(
                    x=df['release_year'],
                    y=df[column],
                    name=name,
                    line=dict(color=colors[i], width=1.5)
                ),
                secondary_y=True
            )
        
        fig.update_layout(
            title="Musical Trends Over Time (1990-Present)",
            template="plotly_dark",
            hovermode="x unified",
            xaxis_title="Release Year",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        fig.update_yaxes(
            title_text="Average Popularity", 
            secondary_y=False,
            range=[0, 100]
        )
        fig.update_yaxes(
            title_text="Audio Feature Values", 
            secondary_y=True,
            range=[0, 1]
        )
        
        self._save_figure(fig, "trends_over_time.html")

    def _generate_time_signature_distribution(self, conn):
        """Generate visualization of time signature distribution and popularity correlation."""
        query = """
        WITH TimeSignatureStats AS (
            SELECT 
                CASE
                    WHEN tf.time_signature = 4 THEN '4/4'
                    WHEN tf.time_signature = 3 THEN '3/4'
                    WHEN tf.time_signature = 5 THEN '5/4'
                    ELSE 'Other'
                END as time_signature_name,
                COUNT(*) as track_count,
                AVG(ar.artist_popularity) as avg_popularity,
                AVG(tf.tempo) as avg_tempo
            FROM track_features tf
            JOIN track_artists ta ON tf.track_id = ta.track_id
            JOIN artists ar ON ta.artist_id = ar.artist_id
            GROUP BY 
                CASE
                    WHEN tf.time_signature = 4 THEN '4/4'
                    WHEN tf.time_signature = 3 THEN '3/4'
                    WHEN tf.time_signature = 5 THEN '5/4'
                    ELSE 'Other'
                END
            ORDER BY track_count DESC
        )
        SELECT *,
            (track_count * 100.0 / SUM(track_count) OVER ()) as percentage
        FROM TimeSignatureStats
        """
        df = pd.read_sql_query(query, conn)
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add bar chart for track count
        fig.add_trace(
            go.Bar(
                x=df['time_signature_name'],
                y=df['percentage'],
                name="% of Tracks",
                marker_color='rgb(158,202,225)',
                opacity=0.6
            ),
            secondary_y=False
        )
        
        # Add line for average popularity
        fig.add_trace(
            go.Scatter(
                x=df['time_signature_name'],
                y=df['avg_popularity'],
                name="Avg Popularity",
                line=dict(color="yellow", width=2),
                mode='lines+markers'
            ),
            secondary_y=True
        )
        
        # Add line for average tempo
        fig.add_trace(
            go.Scatter(
                x=df['time_signature_name'],
                y=df['avg_tempo'],
                name="Avg Tempo (BPM)",
                line=dict(color="red", width=2),
                mode='lines+markers'
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Time Signature Distribution and Musical Characteristics",
            template="plotly_dark",
            hovermode="x unified",
            bargap=0.3,
            xaxis_title="Time Signature",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        fig.update_yaxes(
            title_text="Percentage of Tracks", 
            secondary_y=False,
            range=[0, 100]
        )
        fig.update_yaxes(
            title_text="Average Popularity / Tempo", 
            secondary_y=True
        )
        
        self._save_figure(fig, "time_signatures.html")
class GraphDisplay:
    def __init__(self, graph_generator: GraphGenerator):
        self.graph_generator = graph_generator
        self.categories = graph_generator.get_graph_categories()

    def display_graphs(self):
        """Display graphs with improved UI and error handling."""
        st.markdown("## 📊 Data Insights")

        # Category selection
        category = st.selectbox(
            "Select Analysis Category",
            options=list(self.categories.keys()),
            help="Choose a category of analysis to explore"
        )

        category_data = self.categories[category]
        
        # Graph selection
        selected_graph = st.selectbox(
            "Choose Visualization",
            options=list(category_data.graphs.keys()),
            format_func=lambda x: f"{x} - {category_data.graphs[x].description}"
        )

        graph_data = category_data.graphs[selected_graph]
        st.info(graph_data.description)

        # Display graph
        graph_path = self.graph_generator.output_dir / graph_data.file
        if graph_path.exists():
            self._display_graph(graph_path)
        else:
            self._handle_missing_graph()

    def _display_graph(self, graph_path: Path):
        """Display a graph with error handling."""
        try:
            with open(graph_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=600)
        except Exception as e:
            st.error(f"Error displaying graph: {str(e)}")

    def _handle_missing_graph(self):
        """Handle case when graph file is missing."""
        st.error("Graph not found. Please generate the graphs first.")
        if st.button("Generate Graphs"):
            with st.spinner("Generating graphs..."):
                self.graph_generator.generate_all_graphs()
            st.success("Graphs generated successfully!")
            st.rerun()

def display_saved_graphs():
    """Main entry point for graph display."""
    database = Database()
    graph_generator = GraphGenerator(database)
    graph_display = GraphDisplay(graph_generator)
    graph_display.display_graphs()