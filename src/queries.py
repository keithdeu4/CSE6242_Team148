# queries.py

GET_ARTIST_PROFILE = """
SELECT artist_profiles.*, artists.name as artist_name
FROM artist_profiles
JOIN artists ON artists.id = artist_profiles.artist_id
WHERE artist_profiles.artist_id = ?
"""

GET_ALL_ARTIST_PROFILES = """
SELECT artist_profiles.*, artists.name as artist_name
FROM artist_profiles
JOIN artists ON artists.id = artist_profiles.artist_id
"""

GET_SONGS_FOR_ARTIST = """
SELECT songs.*, audio_features.*, artists.name as artist_name
FROM songs
JOIN audio_features ON songs.track_id = audio_features.track_id
JOIN artists ON artists.id = songs.artist_id
WHERE songs.artist_id = ?
"""
