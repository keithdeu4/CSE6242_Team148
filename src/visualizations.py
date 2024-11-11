from typing import Dict, List, Union
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.decomposition import PCA
from pydantic import BaseModel

class PCAConfig(BaseModel):
    n_components: int = 2
    default_features: Dict[str, float] = {
        "danceability": 0.5,
        "energy": 0.5,
        "acousticness": 0.5,
        "instrumentalness": 0.5,
        "liveness": 0.5,
        "valence": 0.5,
        "loudness": -15.0,
        "popularity": 0.0,
    }
    hover_features: List[str] = [
        "artist_name", "popularity", "danceability", 
        "energy", "acousticness", "valence", "liveness"
    ]

class PCAVisualizer:
    def __init__(self, config: PCAConfig = PCAConfig()):
        self.config = config
        self.pca = PCA(n_components=config.n_components)

    def _convert_to_dict(self, user_preferences: Union[Dict, BaseModel]) -> Dict:
        """Convert user preferences to dictionary if it's a BaseModel."""
        if isinstance(user_preferences, BaseModel):
            return user_preferences.dict()
        return user_preferences

    def prepare_data(
        self, 
        artist_profiles: pd.DataFrame, 
        user_preferences: Union[Dict, BaseModel]
    ) -> tuple[pd.DataFrame, List[str]]:
        """Prepare data for PCA visualization."""
        # Convert user preferences to dictionary if needed
        user_prefs_dict = self._convert_to_dict(user_preferences)

        # Create user preferences DataFrame
        preferences = pd.DataFrame([user_prefs_dict], index=["User"])

        # Add type labels
        artist_profiles = artist_profiles.copy()
        artist_profiles["Type"] = "Artist"
        preferences["Type"] = "User"

        # Combine data
        combined_data = pd.concat(
            [artist_profiles, preferences], 
            ignore_index=False
        ).reset_index(drop=True)

        # Get feature names from user preferences
        feature_names = list(user_prefs_dict.keys())

        # Fill missing values
        for feature in feature_names:
            combined_data[feature] = combined_data[feature].fillna(
                self.config.default_features.get(feature, 0.5)
            )

        return combined_data, feature_names

    def create_pca_dataframe(
        self, 
        combined_data: pd.DataFrame, 
        feature_names: List[str]
    ) -> pd.DataFrame:
        """Create PCA results DataFrame with hover information."""
        # Perform PCA
        pca_results = self.pca.fit_transform(combined_data[feature_names])

        # Create base DataFrame
        pca_df = pd.DataFrame(pca_results, columns=["PCA1", "PCA2"])
        pca_df["Type"] = combined_data["Type"].values
        pca_df["Label"] = combined_data.index

        # Add hover features
        for feature in self.config.hover_features:
            pca_df[feature] = combined_data.get(
                feature, 
                [0.0 if feature != "artist_name" else "Unknown"] * len(combined_data)
            )

        # Create hover info text
        pca_df["hover_info"] = pca_df.apply(
            self._create_hover_text,
            axis=1
        )

        return pca_df

    def _create_hover_text(self, row: pd.Series) -> str:
        """Create hover text for a single data point."""
        hover_text = [f"Name: {row['artist_name']}"]
        
        for feature in self.config.hover_features[1:]:  # Skip artist_name
            if feature == 'popularity':
                hover_text.append(f"{feature.title()}: {row[feature]:.0f}")
            else:
                hover_text.append(f"{feature.title()}: {row[feature]:.2f}")
                
        return "<br>".join(hover_text)

    def create_plot(self, pca_df: pd.DataFrame) -> px.scatter:
        """Create the PCA visualization plot."""
        fig = px.scatter(
            pca_df,
            x="PCA1",
            y="PCA2",
            color="Type",
            color_discrete_map={"User": "red", "Artist": "blue"},
            hover_data={"hover_info": True},
            title="User vs. Artists Preferences",
            labels={"Label": "Entity"},
            symbol="Type"
        )

        # Update hover template
        fig.update_traces(hovertemplate="%{customdata[0]}")

        # Clean up layout
        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            template="plotly_dark"
        )

        return fig

class VisualizationManager:
    def __init__(self):
        self.pca_visualizer = PCAVisualizer()

    def plot_pca_visualization(
        self, 
        artist_profiles: pd.DataFrame, 
        user_preferences: Union[Dict, BaseModel]
    ) -> None:
        """Main function to create and display PCA visualization."""
        try:
            # Prepare data
            combined_data, feature_names = self.pca_visualizer.prepare_data(
                artist_profiles, 
                user_preferences
            )

            # Create PCA DataFrame
            pca_df = self.pca_visualizer.create_pca_dataframe(
                combined_data, 
                feature_names
            )

            # Create and display plot
            fig = self.pca_visualizer.create_plot(pca_df)
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error creating visualization: {str(e)}")

def plot_pca_visualization(
    artist_profiles: pd.DataFrame, 
    user_preferences: Union[Dict, BaseModel]
) -> None:
    """Entry point function for PCA visualization."""
    visualizer = VisualizationManager()
    visualizer.plot_pca_visualization(artist_profiles, user_preferences)