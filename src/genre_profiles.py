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
        """Initialize preset genre profiles with binary values for acousticness, instrumentalness, and liveness."""
        return {
            "Pop": GenreProfile(
                name="Pop",
                description="Catchy melodies with high production values and contemporary sound",
                features={
                    "danceability": 0.7,
                    "energy": 0.7,
                    "acousticness": 0,  # Typically produced electronically
                    "instrumentalness": 0,  # Vocal-focused
                    "valence": 0.65,
                    "liveness": 0,  # Usually studio recordings
                },
                icon="🎵"
            ),
            "Hip Hop": GenreProfile(
                name="Hip Hop",
                description="Rhythm-driven with strong beats and vocal prominence",
                features={
                    "danceability": 0.8,
                    "energy": 0.7,
                    "acousticness": 0,
                    "instrumentalness": 0,  # Vocal-focused
                    "valence": 0.6,
                    "liveness": 0,
                },
                icon="🎤"
            ),
            "Rock": GenreProfile(
                name="Rock",
                description="Guitar-driven with strong rhythms and emotional intensity",
                features={
                    "danceability": 0.5,
                    "energy": 0.8,
                    "acousticness": 0,  # Electric instruments
                    "instrumentalness": 0,  # Vocal-focused
                    "valence": 0.6,
                    "liveness": 1,  # Often live performance elements
                },
                icon="🎸"
            ),
            "R&B": GenreProfile(
                name="R&B",
                description="Smooth, soulful vocals with contemporary production",
                features={
                    "danceability": 0.7,
                    "energy": 0.6,
                    "acousticness": 0,
                    "instrumentalness": 0,  # Vocal-focused
                    "valence": 0.5,
                    "liveness": 0,
                },
                icon="🎹"
            ),
            "Indie": GenreProfile(
                name="Indie",
                description="Alternative sound with emphasis on artistic expression",
                features={
                    "danceability": 0.6,
                    "energy": 0.6,
                    "acousticness": 1,  # Often uses acoustic instruments
                    "instrumentalness": 0,
                    "valence": 0.5,
                    "liveness": 1,
                },
                icon="🎸"
            ),
            "Electronic": GenreProfile(
                name="Electronic",
                description="Synthesizer-based music with strong beats and digital production",
                features={
                    "danceability": 0.8,
                    "energy": 0.8,
                    "acousticness": 0,
                    "instrumentalness": 1,  # Often purely instrumental
                    "valence": 0.6,
                    "liveness": 0,
                },
                icon="⚡"
            ),
            "Latin": GenreProfile(
                name="Latin",
                description="Rhythmic music with Latin American influences",
                features={
                    "danceability": 0.8,
                    "energy": 0.7,
                    "acousticness": 1,  # Often acoustic instruments
                    "instrumentalness": 0,
                    "valence": 0.7,
                    "liveness": 1,
                },
                icon="💃"
            ),
            "Jazz": GenreProfile(
                name="Jazz",
                description="Improvisational with complex harmonies and rhythms",
                features={
                    "danceability": 0.5,
                    "energy": 0.4,
                    "acousticness": 1,
                    "instrumentalness": 1,  # Often instrumental
                    "valence": 0.6,
                    "liveness": 1,  # Often live recordings
                },
                icon="🎷"
            ),
            "Classical": GenreProfile(
                name="Classical",
                description="Orchestral compositions with complex arrangements",
                features={
                    "danceability": 0.3,
                    "energy": 0.4,
                    "acousticness": 1,
                    "instrumentalness": 1,
                    "valence": 0.4,
                    "liveness": 1,
                },
                icon="🎻"
            ),
            "Country": GenreProfile(
                name="Country",
                description="Story-driven songs with traditional American influences",
                features={
                    "danceability": 0.6,
                    "energy": 0.6,
                    "acousticness": 1,
                    "instrumentalness": 0,  # Vocal-focused
                    "valence": 0.7,
                    "liveness": 0,
                },
                icon="🤠"
            ),
            "Metal": GenreProfile(
                name="Metal",
                description="Heavy, intense sound with aggressive instrumentation",
                features={
                    "danceability": 0.4,
                    "energy": 0.9,
                    "acousticness": 0,
                    "instrumentalness": 0,
                    "valence": 0.4,
                    "liveness": 1,
                },
                icon="🤘"
            ),
            "Folk": GenreProfile(
                name="Folk",
                description="Traditional style with acoustic instruments and storytelling",
                features={
                    "danceability": 0.4,
                    "energy": 0.4,
                    "acousticness": 1,
                    "instrumentalness": 0,
                    "valence": 0.5,
                    "liveness": 1,
                },
                icon="🪕"
            ),
            "Alternative": GenreProfile(
                name="Alternative",
                description="Non-mainstream rock with experimental elements",
                features={
                    "danceability": 0.5,
                    "energy": 0.7,
                    "acousticness": 0,
                    "instrumentalness": 0,
                    "valence": 0.5,
                    "liveness": 1,
                },
                icon="🎸"
            ),
            "Blues": GenreProfile(
                name="Blues",
                description="Emotional expression with traditional blues structures",
                features={
                    "danceability": 0.5,
                    "energy": 0.5,
                    "acousticness": 1,
                    "instrumentalness": 0,
                    "valence": 0.4,
                    "liveness": 1,
                },
                icon="🎸"
            ),
            "Reggae": GenreProfile(
                name="Reggae",
                description="Jamaican-influenced with emphasis on off-beat rhythms",
                features={
                    "danceability": 0.7,
                    "energy": 0.5,
                    "acousticness": 1,
                    "instrumentalness": 0,
                    "valence": 0.7,
                    "liveness": 1,
                },
                icon="🌴"
            ),
            "Soul": GenreProfile(
                name="Soul",
                description="Emotionally expressive with R&B influences",
                features={
                    "danceability": 0.6,
                    "energy": 0.5,
                    "acousticness": 1,
                    "instrumentalness": 0,
                    "valence": 0.6,
                    "liveness": 1,
                },
                icon="❤️"
            ),
            "Funk": GenreProfile(
                name="Funk",
                description="Rhythm-heavy with syncopated basslines",
                features={
                    "danceability": 0.8,
                    "energy": 0.7,
                    "acousticness": 0,
                    "instrumentalness": 0,
                    "valence": 0.8,
                    "liveness": 1,
                },
                icon="🕺"
            ),
            "Punk": GenreProfile(
                name="Punk",
                description="Fast-paced, aggressive rock with raw production",
                features={
                    "danceability": 0.5,
                    "energy": 0.9,
                    "acousticness": 0,
                    "instrumentalness": 0,
                    "valence": 0.6,
                    "liveness": 1,
                },
                icon="⚡"
            ),
            "EDM": GenreProfile(
                name="EDM",
                description="Electronic dance music with heavy beats and drops",
                features={
                    "danceability": 0.9,
                    "energy": 0.9,
                    "acousticness": 0,
                    "instrumentalness": 1,
                    "valence": 0.7,
                    "liveness": 0,
                },
                icon="🎧"
            ),
            "Gospel": GenreProfile(
                name="Gospel",
                description="Religious music with strong vocal harmonies",
                features={
                    "danceability": 0.5,
                    "energy": 0.6,
                    "acousticness": 1,
                    "instrumentalness": 0,
                    "valence": 0.8,
                    "liveness": 1,
                },
                icon="🙌"
            ),
            "Ambient": GenreProfile(
                name="Ambient",
                description="Atmospheric, often beatless electronic music",
                features={
                    "danceability": 0.3,
                    "energy": 0.3,
                    "acousticness": 0,
                    "instrumentalness": 1,
                    "valence": 0.4,
                    "liveness": 0,
                },
                icon="🌊"
            ),
            "World": GenreProfile(
                name="World",
                description="Traditional music from various global cultures",
                features={
                    "danceability": 0.6,
                    "energy": 0.6,
                    "acousticness": 1,
                    "instrumentalness": 0,
                    "valence": 0.6,
                    "liveness": 1,
                },
                icon="🌍"
            ),
            "Reggaeton": GenreProfile(
                name="Reggaeton",
                description="Latin urban music with distinctive rhythm",
                features={
                    "danceability": 0.9,
                    "energy": 0.8,
                    "acousticness": 0,
                    "instrumentalness": 0,
                    "valence": 0.7,
                    "liveness": 0,
                },
                icon="🔥"
            ),
            "K-pop": GenreProfile(
                name="K-pop",
                description="Korean pop music with complex productions",
                features={
                    "danceability": 0.8,
                    "energy": 0.8,
                    "acousticness": 0,
                    "instrumentalness": 0,
                    "valence": 0.7,
                    "liveness": 0,
                },
                icon="💫"
            ),
            "Trap": GenreProfile(
                name="Trap",
                description="Hip-hop subgenre with heavy bass and hi-hats",
                features={
                    "danceability": 0.8,
                    "energy": 0.7,
                    "acousticness": 0,
                    "instrumentalness": 0,
                    "valence": 0.5,
                    "liveness": 0,
                },
                icon="💎"
            )
        }