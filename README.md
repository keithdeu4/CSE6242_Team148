# Personalized Spotify Playlist Generator 🎵

This is a Streamlit-based application that recommends personalized playlists based on user preferences and visualizes artist similarity. Using PyVis and Plotly for interactive visualizations and a custom recommendation model, the app provides tailored music suggestions and displays similar artists in an intuitive interface.

## Features
- **Personalized Recommendations**: Adjust music feature preferences (danceability, energy, acousticness, etc.) and get tailored artist and song recommendations.
- **Artist Similarity Visualization**: Explore relationships between artists with a PyVis network graph and see how they relate to your chosen preferences.
- **Cluster Analysis**: View your preferences plotted against artist profiles with PCA, showing how your musical taste fits into the broader landscape.
- **Interactive Chat Interface**: Engage with the app through a chat interface to request recommendations, view song suggestions, and explore similar artists.

## Prerequisites
- **Python 3.7 or higher**
- **Poetry** for package management
- **Spotify Dataset** in a SQLite database (`music_data.db`) that includes:
  - Artist profiles with musical features (e.g., danceability, energy, etc.)
  - Songs with audio features for recommendation

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/spotify-playlist-generator.git
   cd spotify-playlist-generator

2. **Set Up the Virtual Environment Using Poetry**:
    If you haven't installed Poetry, you can do so by following the instructions at https://python-poetry.org/docs/#installation.
    Run the following command to install dependencies and set up the environment:
    ``bash
    poetry install

3. **Activate the Virtual Environment**:
    ```bash
    poetry shell

4. **Prepare the database**:
- Ensure music_data.db is available in the root directory, with required tables for artist profiles and song features.

5. **Run the  Streamlit App**:
    ```bash
    streamlit run src/app.py

## Usage
- **Adjust Music Preferences**: Use the sidebar sliders to set your preferences for different musical features.
- **Get Recommendations**: Click "Find Matching Artists" to receive artist recommendations based on your preferences.
- **Explore Similar Artists**: Select an artist from the recommendations, and the app will display similar artists in a network graph.
- **Cluster Analysis**: Switch to the "Cluster Analysis" tab to view how your preferences compare to artist profiles with a PCA visualization.
- **Data Insights**: The "Data Insights" tab provides visualizations of saved graphs for deeper analysis.

## Project Structure TODO: Update
spotify-playlist-generator/
├── src/
│   ├── app.py                 # Main Streamlit app
│   ├── chatbot.py             # Chatbot functionality
│   ├── database.py            # Database connection and queries
│   ├── queries.py             # SQL queries for database operations
│   ├── state_management.py    # Session state initialization
│   ├── visualizations.py      # PCA and plot visualizations
│   └── graphs.py              # Functions for displaying saved graphs
├── music_data.db              # SQLite database with Spotify data
├── pyproject.toml             # Poetry configuration file
└── README.md                  # Project documentation

## Dependencies
- **Streamlit**: For building the web application interface.
- **Pandas**: For data manipulation and handling.
- **Plotly**: For interactive data visualizations.
- **PyVis**: For network graph visualization.
- **scikit-learn**: For performing PCA.

Dependencies are managed through Poetry, and they will be installed by running `poetry install`.

## License
This project is licensed under the MIT License.
