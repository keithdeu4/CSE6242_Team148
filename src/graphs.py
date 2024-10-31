import os

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------
# Pre-generate Graphs
# ---------------------------------------------
def generate_and_save_graphs(songs_df, artist_profiles):
    # Create output directory if it doesn't exist
    output_dir = "graphs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Popularity Distribution
    fig = px.histogram(artist_profiles, x="popularity", title="Popularity Distribution")
    fig.update_traces(marker=dict(color="blue"))
    fig.write_html(os.path.join(output_dir, "popularity_distribution.html"))

    # Danceability vs Popularity
    fig = px.scatter(
        artist_profiles,
        x="danceability",
        y="popularity",
        title="Danceability vs Popularity",
        color="artist_name",
        hover_name="artist_name",
    )
    fig.update_traces(marker=dict(opacity=0.7))
    fig.write_html(os.path.join(output_dir, "danceability_vs_popularity.html"))

    # Energy Distribution
    fig = px.box(artist_profiles, y="energy", title="Energy Distribution by Artist")
    fig.update_traces(marker=dict(color="green"))
    fig.write_html(os.path.join(output_dir, "energy_distribution.html"))

    # Acousticness Distribution
    fig = px.histogram(
        artist_profiles, x="acousticness", title="Acousticness Distribution"
    )
    fig.update_traces(marker=dict(color="orange"))
    fig.write_html(os.path.join(output_dir, "acousticness_distribution.html"))

    # Valence vs Energy
    fig = px.scatter(
        artist_profiles,
        x="valence",
        y="energy",
        title="Valence vs Energy",
        color="artist_name",
        hover_name="artist_name",
    )
    fig.update_traces(marker=dict(opacity=0.7))
    fig.write_html(os.path.join(output_dir, "valence_vs_energy.html"))

    # Number of Songs by Genre
    genre_counts = songs_df["genre"].value_counts().reset_index()
    genre_counts.columns = ["Genre", "Number of Songs"]
    fig = px.bar(
        genre_counts, x="Genre", y="Number of Songs", title="Number of Songs by Genre"
    )
    fig.update_traces(marker=dict(color="purple"))
    fig.write_html(os.path.join(output_dir, "number_of_songs_by_genre.html"))

    # Artist Song Count
    artist_counts = songs_df["artist_name"].value_counts().reset_index()
    artist_counts.columns = ["Artist", "Number of Songs"]
    fig = px.bar(
        artist_counts,
        x="Artist",
        y="Number of Songs",
        title="Number of Songs by Artist",
    )
    fig.update_traces(marker=dict(color="red"))
    fig.write_html(os.path.join(output_dir, "number_of_songs_by_artist.html"))

    # Duration Distribution
    fig = px.histogram(
        songs_df,
        x="duration_ms",
        nbins=30,
        title="Song Duration Distribution",
        labels={"duration_ms": "Duration (ms)"},
    )
    fig.update_traces(marker=dict(color="cyan"))
    fig.write_html(os.path.join(output_dir, "duration_distribution.html"))

    # Danceability vs Energy
    fig = px.scatter(
        songs_df,
        x="danceability",
        y="energy",
        color="genre",
        title="Danceability vs Energy by Genre",
        hover_name="artist_name",
    )
    fig.update_traces(marker=dict(opacity=0.7))
    fig.write_html(os.path.join(output_dir, "danceability_vs_energy.html"))

    # Energy vs Acousticness
    fig = px.scatter(
        songs_df,
        x="energy",
        y="acousticness",
        color="artist_name",
        title="Energy vs Acousticness",
        hover_name="song_name",
    )
    fig.update_traces(marker=dict(opacity=0.7))
    fig.write_html(os.path.join(output_dir, "energy_vs_acousticness.html"))

    # Valence vs Popularity
    fig = px.scatter(
        songs_df,
        x="valence",
        y="popularity",
        color="genre",
        title="Valence vs Popularity by Genre",
        hover_name="song_name",
    )
    fig.update_traces(marker=dict(opacity=0.7))
    fig.write_html(os.path.join(output_dir, "valence_vs_popularity.html"))


def display_saved_graphs():
    st.markdown("## 📊 Data Insights")
    st.write("Explore various attributes of the artist and song data:")

    # Dropdown menu for selecting the attribute to visualize
    attribute = st.selectbox(
        "Choose an attribute to visualize",
        [
            "Popularity Distribution",
            "Danceability vs Popularity",
            "Energy Distribution",
            "Acousticness Distribution",
            "Valence vs Energy",
            "Number of Songs by Genre",
            "Number of Songs by Artist",
            "Duration Distribution",
            "Danceability vs Energy",
            "Energy vs Acousticness",
            "Valence vs Popularity",
        ],
    )

    # Dictionary mapping attributes to corresponding HTML files
    graph_files = {
        "Popularity Distribution": "popularity_distribution.html",
        "Danceability vs Popularity": "danceability_vs_popularity.html",
        "Energy Distribution": "energy_distribution.html",
        "Acousticness Distribution": "acousticness_distribution.html",
        "Valence vs Energy": "valence_vs_energy.html",
        "Number of Songs by Genre": "number_of_songs_by_genre.html",
        "Number of Songs by Artist": "number_of_songs_by_artist.html",
        "Duration Distribution": "duration_distribution.html",
        "Danceability vs Energy": "danceability_vs_energy.html",
        "Energy vs Acousticness": "energy_vs_acousticness.html",
        "Valence vs Popularity": "valence_vs_popularity.html",
    }

    # Display the selected graph
    graph_path = os.path.join("graphs", graph_files[attribute])
    if os.path.exists(graph_path):
        with open(graph_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=600)
    else:
        st.write("Graph not found. Please make sure to generate the graphs first.")
