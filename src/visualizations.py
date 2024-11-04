import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.decomposition import PCA


def plot_pca_visualization(artist_profiles, user_preferences):
    """Perform PCA and plot the user preferences against artist profiles.

    Args:
        artist_profiles (pd.DataFrame): DataFrame with artist profile data.
        user_preferences (dict): User's music feature preferences.

    Returns:
        plotly.graph_objects.Figure: Scatter plot with PCA components.
    """
    # Create a DataFrame from user preferences
    preferences = pd.DataFrame([user_preferences], index=["User"])

    # Ensure `Type` column exists in both DataFrames
    artist_profiles = artist_profiles.copy()
    artist_profiles["Type"] = "Artist"
    preferences["Type"] = "User"

    # Concatenate artist profiles with user preferences and check feature alignment
    combined_data = pd.concat(
        [artist_profiles, preferences], ignore_index=False
    ).reset_index(drop=True)
    feature_names = list(
        user_preferences.keys()
    )  # Ensure feature_names are columns present in combined data

    # Ensure the combined data does not have NaNs in feature columns
    if combined_data[feature_names].isnull().values.any():
        st.error(
            "Combined data contains NaN values. Please ensure all features are numeric and present."
        )
        return

    # Perform PCA on feature columns
    pca = PCA(n_components=2)
    pca_results = pca.fit_transform(combined_data[feature_names])

    # Create DataFrame for PCA results
    pca_df = pd.DataFrame(pca_results, columns=["PCA1", "PCA2"])
    pca_df["Type"] = combined_data["Type"].values
    pca_df["Label"] = combined_data.index
    # Add columns for hover info details (example values below; replace with your actual data structure)
    pca_df["artist_name"] = combined_data["artist_name"]
    pca_df["popularity"] = combined_data.get("popularity", [0] * len(combined_data))
    pca_df["danceability"] = combined_data.get(
        "danceability", [0.0] * len(combined_data)
    )
    pca_df["energy"] = combined_data.get("energy", [0.0] * len(combined_data))
    pca_df["acousticness"] = combined_data.get(
        "acousticness", [0.0] * len(combined_data)
    )
    pca_df["valence"] = combined_data.get("valence", [0.0] * len(combined_data))
    pca_df["liveness"] = combined_data.get("liveness", [0.0] * len(combined_data))

    # Create hover info text for each point using the specified format
    pca_df["hover_info"] = pca_df.apply(
        lambda artist: (
            f"Name: {artist['artist_name']}<br>"
            f"Popularity: {artist['popularity']:.0f}<br>"
            f"Danceability: {artist['danceability']:.2f}<br>"
            f"Energy: {artist['energy']:.2f}<br>"
            f"Acousticness: {artist['acousticness']:.2f}<br>"
            f"Valence: {artist['valence']:.2f}<br>"
            f"Liveness: {artist['liveness']:.2f}"
        ),
        axis=1,
    )

    # Define color mapping for User to red, Artist to another color
    color_discrete_map = {"User": "red", "Artist": "blue"}

    # Plotly scatter plot for clusters with custom hover info
    fig = px.scatter(
        pca_df,
        x="PCA1",
        y="PCA2",
        color="Type",
        color_discrete_map=color_discrete_map,
        hover_data={"hover_info": True},
        title="User vs. Artists Preferences",
        labels={"Label": "Entity"},
        symbol="Type",
    )

    # Update hover to use only custom hover_info
    fig.update_traces(hovertemplate="%{customdata[0]}")

    # Remove X and Y axis labels, ticks, and grid lines
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    )

    # Display plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)
