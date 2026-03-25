import json
from pathlib import Path
import random
from typing import Any

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

def load_users():
    """
    Loads users from data/users.sample.json
    Returns a lits of user dictionaries.
    """
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "data" /"users.sample.json"

    with open(path, "r", encoding = "utf-8") as f:
        users = json.load(f)
    return users

def save_users(data):
    """
    Saves users to data/users.sample.json
    """
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "data" /"users.sample.json"

    with open(path, "w", encoding = "utf-8") as f:
        json.dump(data, f, indent=4)

def update_user_preferences(user_id: str, song: dict, liked: bool):
    users: Any = load_users()
    user_record: dict[str, Any]

    if isinstance(users, dict):
        if user_id not in users or not isinstance(users[user_id], dict):
            users[user_id] = {"liked_genres": [], "disliked_genres": []}
        user_record = users[user_id]
    elif isinstance(users, list):
        found_record: dict[str, Any] | None = None
        for item in users:
            if isinstance(item, dict) and item.get("user_id") == user_id:
                found_record = item
                break

        if found_record is None:
            user_record = {"user_id": user_id}
            users.append(user_record)
        else:
            user_record = found_record
    else:
        raise TypeError("Users data must be a dict or list of dicts")

    user_record.setdefault("liked_genres", [])
    user_record.setdefault("disliked_genres", [])
    target = "liked_genres" if liked else "disliked_genres"

    for genre in song.get("genres", []):
        if genre not in user_record[target]:
            user_record[target].append(genre)
    save_users(users)

