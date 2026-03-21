import json
from pathlib import Path
import random

def load_songs() -> list:
    """
    Loads songs from data/songs.sample.json
    Returns a lits of song dictionaries.
    """
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" /"songs.sample.json"
    with open(data_path, "r", encoding = "utf-8") as f:
        songs = json.load(f)
    return songs

def filter_songs_by_genres(songs: list, genres: list) -> list:
    """
    Filters songs whose genre matches any in the given genre list.
    """
    filtered = []
    for song in songs:
        song_genres = song.get("genres", [])
        
        # check if ANY genre overlaps between song and bucket genres
        if any(genre in song_genres for genre in genres):
            filtered.append(song)
    return filtered

def pick_random_songs(songs: list, k: int = 5) -> list:
    """
    Picks k random songs from the given list.
    If there are fewer than n songs, returns all of them.
    """
    if len(songs) <= k:
        return songs
    return random.sample(songs, k)

def recommend_songs_for_genres(genres: list, k: int = 5) -> list:
    """
    Recommends songs based on the given genres.
    Loads songs from data/songs.sample.json, filters by genres, and picks k random ones.
    """
    songs = load_songs()
    filtered = filter_songs_by_genres(songs, genres)
    return pick_random_songs(filtered, k)

