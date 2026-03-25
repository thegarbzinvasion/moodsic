import json
from pathlib import Path
import random
from typing import Any
from moodsic.ml_model import train_model 

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

def pick_random_songs(songs: list, k: int = 4) -> list:
    """
    Picks k random songs from the given list.
    If there are fewer than n songs, returns all of them.
    """
    if len(songs) <= k:
        return songs
    return random.sample(songs, k)

def recommend_songs_for_genres(genres: list, user_id: str, k: int = 4) -> list:
    """
    Recommends songs based on the given genres.
    Loads songs from data/songs.sample.json, filters by genres, and picks k random ones.
    """
    songs = load_songs()
    filtered = filter_songs_by_genres(songs, genres)

    prefs = get_user_preferences(user_id)
    liked = prefs["liked_genres"]
    disliked = prefs["disliked_genres"]
    model, vec = train_model()

    # Score all songs
    scored = []
    for song in filtered:

        base_score = score_song(song, liked, disliked)
        if model is None or vec is None:
            ml_score = 0

        if model and vec:
            song_features = [{"genre": g} for g in song.get("genres", [])]
            song_features_any: Any = song_features
            X_vec = vec.transform(song_features_any)

            preds = model.predict(X_vec)    

            # Average prediction across genres
            ml_score = sum(preds) / len(preds)
        
        final_score = base_score + ml_score
        scored.append((final_score, song))

    #Sort by score (highest first)
    scored.sort(key=lambda x: x[0], reverse=True)

    # Extract songs only
    ranked_songs = [song for _, song in scored]

    # Return top k 
    return ranked_songs[:k]

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
    """
    Updates the user prefenences depending on whether they liked or disliked a song.
        - If liked, add all genres of the song to the user's "liked_genres" list (if not already present)
        - If disliked, add all genres of the song to the user's "disliked_genres" list (if not already present)
    """
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

def get_user_preferences(user_id: str):
    """
    Retrieves the user's liked and disliked genres.
    Returns a dict with "liked_genres" and "disliked_genres" lists.
    """
    users = load_users()

    if isinstance(users, dict):
        return users.get(user_id, {"liked_genres": [], "disliked_genres": []})

    if isinstance(users, list):
        for item in users:
            if isinstance(item, dict) and item.get("user_id") == user_id:
                return {
                    "liked_genres": item.get("liked_genres", []),
                    "disliked_genres": item.get("disliked_genres", []),
                }
        return {"liked_genres": [], "disliked_genres": []}

    return {"liked_genres": [], "disliked_genres": []}

def score_song(song: dict, liked: list, disliked: list) -> int:
    """
    Scores a song based on the user's liked and disliked genres.
    +2 for each genre in the song that is in the liked list, -1 for each genre in the disliked list.
    Returns the total score for the song.
    """
    score = 0

    for genre in song.get("genres", []):
        if genre in liked:
            score += 2 # reward
        if genre in disliked:
            score -= 1 # penalty 
    return score

def log_interaction(song: dict, liked: bool):
    """
    Logs the user's interaction with a song to data/interactions.json
    Each entry should include the song's genres and whether the user liked or disliked it.
    """
    import json
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "data" / "interactions.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for genre in song.get("genres", []):
        data.append({
            "genre": genre,
            "liked": 1 if liked else 0
        })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)