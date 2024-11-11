# models.py
from typing import List, Dict, Optional, Set
from pydantic import BaseModel, Field
import pandas as pd

class Song(BaseModel):
    track_name: str
    artist_name: str
    album_image_url: str
    album_name: str
    popularity: int
    uri: str
    track_external_url: str

    @classmethod
    def from_series(cls, series: pd.Series) -> 'Song':
        """Create Song instance from pandas Series with proper type conversion."""
        return cls(
            track_name=str(series["track_name"]),
            artist_name=str(series["artist_name"]),
            album_image_url=str(series["album_image_url"]),
            album_name=str(series["album_name"]),
            popularity=int(series["popularity"]),
            uri=str(series["uri"]),
            track_external_url=str(series["track_external_url"])
        )

    class Config:
        from_attributes = True

class AudioFeature(BaseModel):
    name: str
    type: str
    min_value: float = Field(default=0.0)
    max_value: float = Field(default=1.0)
    step: float = Field(default=0.01)
    default: float = Field(default=0.5)
    labels: Optional[List[str]] = None
    description: str = Field(default="")
    options: Optional[List[str]] = None

class UserPreferences(BaseModel):
    danceability: float = Field(default=0.5, ge=0.0, le=1.0)
    energy: float = Field(default=0.5, ge=0.0, le=1.0)
    acousticness: float = Field(default=0.5, ge=0.0, le=1.0)
    instrumentalness: float = Field(default=0.5, ge=0.0, le=1.0)
    liveness: float = Field(default=0.5, ge=0.0, le=1.0)
    valence: float = Field(default=0.5, ge=0.0, le=1.0)
    loudness: float = Field(default=-15.0, ge=-30.0, le=0.0)
    popularity: int = Field(default=50, ge=0, le=100)