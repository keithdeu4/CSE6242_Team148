# queries.py

GET_ARTIST_PROFILE = """
SELECT artist_profiles.*, artists.artist_name, artists.artist_popularity, artists.artist_image_url
FROM artist_profiles
JOIN artists ON artists.artist_id = artist_profiles.artist_id
WHERE artist_profiles.artist_id = ?
"""

GET_ALL_ARTIST_PROFILES = """
SELECT artist_profiles.*, artists.artist_name, artists.artist_popularity, artists.artist_image_url
FROM artist_profiles
JOIN artists ON artists.artist_id = artist_profiles.artist_id
"""

GET_SONGS_FOR_ARTIST = """
SELECT tracks.*, track_features.*, artists.artist_name, albums.album_image_url
FROM tracks
JOIN track_features ON tracks.track_id = track_features.track_id
JOIN track_artists ON track_artists.track_id = tracks.track_id
JOIN artists ON artists.artist_id = track_artists.artist_id
JOIN albums on tracks.album_id = albums.album_id
WHERE artists.artist_id = ?
"""
