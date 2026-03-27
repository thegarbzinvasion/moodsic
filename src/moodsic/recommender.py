import json
from pathlib import Path
import random
from typing import Any
from moodsic.ml_model import train_model 
from moodsic.user_history import get_user_history, get_excluded_songs, add_to_history

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
    Uses hybrid approach: Last.fm first, then local sample data as fallback.
    """
    # Try Last.fm first - ask for more variety
    lastfm_songs = []
    try:
        from moodsic.lastfm_client import lastfm_client
        
        # Get more songs than needed for variety
        # If user has history, we can use their preferences to filter
        tracks_per_genre = max(3, (k * 2) // len(genres)) if genres else k
        
        lastfm_songs = lastfm_client.get_tracks_by_multiple_tags(
            genres, 
            limit_per_tag=tracks_per_genre
        )
        
        print(f"Found {len(lastfm_songs)} songs from Last.fm")
        
        # Add source tag and ensure image_url exists
        for song in lastfm_songs:
            song["source"] = "lastfm"
            if "image_url" not in song:
                song["image_url"] = None
            
    except Exception as e:
        print(f"Last.fm error: {e}")
    
    # If Last.fm gave us enough songs, return them (already randomized)
    if len(lastfm_songs) >= k:
        # Randomize again to ensure variety
        import random
        random.shuffle(lastfm_songs)
        return lastfm_songs[:k]
    
    # Otherwise, supplement with local songs
    remaining_needed = k - len(lastfm_songs)
    print(f"Need {remaining_needed} more songs from local database")
    
    # Load and filter local songs
    songs = load_songs()
    filtered = filter_songs_by_genres(songs, genres)
    
    # Remove any songs that were already recommended by Last.fm
    lastfm_ids = {s["id"] for s in lastfm_songs}
    filtered = [s for s in filtered if s["id"] not in lastfm_ids]
    
    if not filtered:
        return lastfm_songs[:k]
    
    # Score local songs using user preferences and ML model
    prefs = get_user_preferences(user_id)
    liked = prefs["liked_genres"]
    disliked = prefs["disliked_genres"]
    model, vec = train_model()
    
    scored = []
    for song in filtered:
        base_score = score_song(song, liked, disliked)
        
        ml_score = 0
        if model is not None and vec is not None:
            # Create features for each genre
            song_features = []
            for genre in song.get("genres", []):
                song_features.append({"genre": genre})
            
            if song_features:
                try:
                    X_vec = vec.transform(song_features)
                    preds = model.predict(X_vec)
                    ml_score = sum(preds) / len(preds) if preds.size > 0 else 0
                except Exception as e:
                    print(f"ML prediction error: {e}")
                    ml_score = 0
        
        final_score = base_score + ml_score
        scored.append((final_score, song))
    
    # Sort and get top local songs
    scored.sort(key=lambda x: x[0], reverse=True)
    ranked_local_songs = [song for _, song in scored]
    
    # Add source tag and ensure image_url exists for local songs
    for song in ranked_local_songs:
        song["source"] = "local"
        if "image_url" not in song:
            song["image_url"] = None
    
    # Shuffle local songs for variety before combining
    import random
    random.shuffle(ranked_local_songs)
    
    # Combine: Last.fm songs first, then fill with local songs
    combined = lastfm_songs + ranked_local_songs
    
    # Final shuffle for variety
    random.shuffle(combined[:k])
    
    return combined[:k]

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

    from moodsic.user_history import add_to_history
    add_to_history(user_id, song, "liked" if liked else "disliked")

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
    
    # Handle case where genres might not exist or is None
    genres = song.get("genres", [])
    if not genres:
        return 0
    
    for genre in genres:
        if genre in liked:
            score += 2
        if genre in disliked:
            score -= 1
    return score

def log_interaction(song: dict, liked: bool):
    """Logs the user's interaction with a song to data/interactions.json"""
    import json
    from pathlib import Path
    from moodsic.user_history import add_to_history

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
    
    # Also track in user history
    user_id = "user_1"  # You might want to pass this as a parameter
    add_to_history(user_id, song, "liked" if liked else "disliked")

def clear_user_history(user_id: str):
    """Clear user's history to reset recommendations"""
    from moodsic.user_history import save_user_history
    save_user_history(user_id, {"liked_songs": [], "disliked_songs": [], "recommended_songs": []})