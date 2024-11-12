from pydantic import BaseModel
from typing import Dict

class GenreProfile(BaseModel):
    name: str
    description: str
    features: Dict[str, float]
    icon: str

class GenreProfileManager:
    @staticmethod
    def get_profiles() -> Dict[str, GenreProfile]:
        """Initialize preset genre profiles."""
        return {
            "Pop": GenreProfile(
                name="Pop",
                description="Catchy melodies with high production values and contemporary sound",
                features={
                    "danceability": 0.7,
                    "energy": 0.7,
                    "acousticness": 0.2,
                    "instrumentalness": 0.0,
                    "valence": 0.65,
                    "liveness": 0.2,
                },
                icon="🎵"
            ),
            "Rock": GenreProfile(
                name="Rock",
                description="Guitar-driven with strong rhythms and emotional intensity",
                features={
                    "danceability": 0.5,
                    "energy": 0.8,
                    "acousticness": 0.3,
                    "instrumentalness": 0.1,
                    "valence": 0.6,
                    "liveness": 0.4,
                },
                icon="🎸"
            ),
            "Electronic": GenreProfile(
                name="Electronic",
                description="Synthesizer-based music with strong beats and digital production",
                features={
                    "danceability": 0.8,
                    "energy": 0.8,
                    "acousticness": 0.1,
                    "instrumentalness": 0.6,
                    "valence": 0.6,
                    "liveness": 0.2,
                },
                icon="⚡"
            ),
            "Classical": GenreProfile(
                name="Classical",
                description="Orchestral compositions with complex arrangements",
                features={
                    "danceability": 0.3,
                    "energy": 0.4,
                    "acousticness": 0.9,
                    "instrumentalness": 0.9,
                    "valence": 0.4,
                    "liveness": 0.3,
                },
                icon="🎻"
            ),
            "Jazz": GenreProfile(
                name="Jazz",
                description="Improvisational with complex harmonies and rhythms",
                features={
                    "danceability": 0.5,
                    "energy": 0.4,
                    "acousticness": 0.7,
                    "instrumentalness": 0.4,
                    "valence": 0.6,
                    "liveness": 0.4,
                },
                icon="🎷"
            ),
            "Hip Hop": GenreProfile(
                name="Hip Hop",
                description="Rhythm-driven with strong beats and vocal prominence",
                features={
                    "danceability": 0.8,
                    "energy": 0.7,
                    "acousticness": 0.2,
                    "instrumentalness": 0.0,
                    "valence": 0.6,
                    "liveness": 0.3,
                },
                icon="🎤"
            )
        }