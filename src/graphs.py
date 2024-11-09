import os
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
from database import get_connection

conn = get_connection()

def generate_and_save_graphs(conn):
    """
    Generate and save graphs using data from connected database, with optimizations for large datasets
    """
    output_dir = "graphs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get top artists by popularity (limit to top 50 for clearer visualizations)
    top_artists_query = """
    SELECT artist_id, artist_name, artist_popularity, artist_followers 
    FROM artists 
    ORDER BY artist_popularity DESC 
    LIMIT 50
    """
    top_artists = pd.read_sql_query(top_artists_query, conn)
    top_artist_ids = tuple(top_artists['artist_id'])

    # Get combined track data for only top artists
    tracks_query = f"""
    SELECT 
        t.track_id, t.track_name, t.popularity, t.duration_ms, t.explicit,
        t.time_signature, 
        a.album_name, a.release_date, a.album_image_url,
        ar.artist_name, ar.artist_popularity, ar.artist_followers,
        tf.danceability, tf.energy, tf.loudness, tf.acousticness,
        tf.instrumentalness, tf.liveness, tf.valence, tf.tempo
    FROM tracks t
    JOIN track_artists ta ON t.track_id = ta.track_id
    JOIN artists ar ON ta.artist_id = ar.artist_id
    JOIN albums a ON t.album_id = a.album_id
    JOIN track_features tf ON t.track_id = tf.track_id
    WHERE ar.artist_id IN {top_artist_ids}
    """
    tracks_df = pd.read_sql_query(tracks_query, conn)

    # 1. Artist Popularity Distribution
    popularity_query = """
    SELECT 
        ROUND(artist_popularity/10.0)*10 as popularity_bracket,
        COUNT(*) as count
    FROM artists
    GROUP BY ROUND(artist_popularity/10.0)*10
    ORDER BY popularity_bracket
    """
    popularity_dist = pd.read_sql_query(popularity_query, conn)
    
    fig = px.bar(
        popularity_dist,
        x="popularity_bracket",
        y="count",
        title="Artist Popularity Distribution",
        labels={
            "popularity_bracket": "Popularity Score (Brackets of 10)",
            "count": "Number of Artists"
        },
        template="plotly_dark"
    )
    fig.write_html(os.path.join(output_dir, "popularity_distribution.html"))

    # 2. Follower Distribution
    follower_query = """
    SELECT 
        ROUND(artist_popularity/10.0)*10 as popularity_bracket,
        AVG(artist_followers) as avg_followers,
        COUNT(*) as artist_count
    FROM artists
    GROUP BY ROUND(artist_popularity/10.0)*10
    ORDER BY popularity_bracket
    """
    follower_dist = pd.read_sql_query(follower_query, conn)
    
    fig = px.scatter(
        follower_dist,
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
    fig.write_html(os.path.join(output_dir, "followers_by_popularity.html"))

    # 3. Audio Features Distribution
    feature_query = """
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
    feature_dist = pd.read_sql_query(feature_query, conn)
    
    fig = px.violin(
        feature_dist,
        x="feature",
        y="value",
        title="Distribution of Audio Features Across All Artists",
        box=True,
        template="plotly_dark"
    )
    fig.write_html(os.path.join(output_dir, "feature_distributions.html"))

    # 4. Top Artists Comparison
    top_artists_features = tracks_df.groupby('artist_name').agg({
        'danceability': 'mean',
        'energy': 'mean',
        'acousticness': 'mean',
        'valence': 'mean',
        'popularity': 'mean'
    }).round(3)

    fig = px.parallel_coordinates(
        top_artists_features.reset_index(),
        title="Audio Features of Top Artists",
        dimensions=['danceability', 'energy', 'acousticness', 'valence', 'popularity'],
        template="plotly_dark"
    )
    fig.write_html(os.path.join(output_dir, "top_artists_features.html"))

    # 5. Time Signatures
    time_sig_query = """
    SELECT 
        time_signature,
        COUNT(*) as count,
        AVG(popularity) as avg_popularity
    FROM tracks
    GROUP BY time_signature
    ORDER BY count DESC
    """
    time_sig_dist = pd.read_sql_query(time_sig_query, conn)
    
    fig = px.bar(
        time_sig_dist,
        x="time_signature",
        y="count",
        color="avg_popularity",
        title="Time Signature Distribution",
        labels={
            "time_signature": "Time Signature",
            "count": "Number of Tracks",
            "avg_popularity": "Average Popularity"
        },
        template="plotly_dark"
    )
    fig.write_html(os.path.join(output_dir, "time_signatures.html"))

    # 6. Release Year Trends
    year_query = """
    SELECT 
        SUBSTR(release_date, 1, 4) as year,
        COUNT(*) as track_count,
        AVG(t.popularity) as avg_popularity,
        AVG(tf.danceability) as avg_danceability,
        AVG(tf.energy) as avg_energy
    FROM albums a
    JOIN tracks t ON a.album_id = t.album_id
    JOIN track_features tf ON t.track_id = tf.track_id
    WHERE SUBSTR(release_date, 1, 4) >= '1900'
    GROUP BY SUBSTR(release_date, 1, 4)
    ORDER BY year
    """
    year_stats = pd.read_sql_query(year_query, conn)
    
    fig = px.line(
        year_stats,
        x="year",
        y=["avg_popularity", "avg_danceability", "avg_energy"],
        title="Trends Over Time",
        labels={
            "year": "Release Year",
            "value": "Average Value",
            "variable": "Metric"
        },
        template="plotly_dark"
    )
    fig.write_html(os.path.join(output_dir, "trends_over_time.html"))

def display_saved_graphs():
    """
    Display the saved graphs in a structured, categorized manner
    """
    st.markdown("## 📊 Data Insights")
    
    # Define categories and their descriptions
    categories = {
        "Overall Statistics": {
            "Popularity Distribution": {
                "file": "popularity_distribution.html",
                "description": "Distribution of artist popularity scores across the platform"
            },
            "Followers by Popularity": {
                "file": "followers_by_popularity.html",
                "description": "Relationship between artist popularity and follower count"
            },
            "Feature Distributions": {
                "file": "feature_distributions.html",
                "description": "Distribution of audio features across all artists"
            }
        },
        "Top Artists Analysis": {
            "Top Artists Features": {
                "file": "top_artists_features.html",
                "description": "Parallel coordinates plot comparing features of top artists"
            },
            "Trends Over Time": {
                "file": "trends_over_time.html",
                "description": "Historical trends in popularity and audio features"
            }
        },
        "Musical Characteristics": {
            "Time Signatures": {
                "file": "time_signatures.html",
                "description": "Distribution of time signatures and their correlation with popularity"
            }
        }
    }
    
    # Category selection
    category = st.selectbox(
        "Select Analysis Category",
        options=list(categories.keys()),
        help="Choose a category of analysis to explore"
    )
    
    # Graph selection within category
    selected_graph = st.selectbox(
        "Choose Visualization",
        options=list(categories[category].keys()),
        format_func=lambda x: f"{x} - {categories[category][x]['description']}"
    )
    
    # Display description
    st.info(categories[category][selected_graph]['description'])
    
    # Display selected graph
    graph_path = Path("assets/graphs") / categories[category][selected_graph]['file']
    if graph_path.exists():
        with open(graph_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=600)
    else:
        st.error(f"Graph not found at {graph_path}. Please generate the graphs first.")
        if st.button("Generate Graphs"):
            with st.spinner("Generating graphs..."):
                generate_and_save_graphs(st.session_state.conn)
            st.success("Graphs generated successfully!")
            st.rerun()