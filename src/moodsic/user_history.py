import json
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

def get_user_history(user_id: str) -> Dict:
    """Load user's interaction history"""
    project_root = Path(__file__).resolve().parents[2]
    history_path = project_root / "data" / f"{user_id}_history.json"
    
    if history_path.exists():
        with open(history_path, "r") as f:
            return json.load(f)
    else:
        return {"liked_songs": [], "disliked_songs": [], "recommended_songs": []}

def save_user_history(user_id: str, history: Dict):
    """Save user's interaction history"""
    project_root = Path(__file__).resolve().parents[2]
    history_path = project_root / "data" / f"{user_id}_history.json"
    
    with open(history_path, "w") as f:
        json.dump(history, f, indent=4)

def add_to_history(user_id: str, song: Dict, action: str):
    """Add song to user's history (liked, disliked, or recommended)"""
    history = get_user_history(user_id)
    
    if action == "liked":
        # Don't add duplicates
        if song["id"] not in [s["id"] for s in history["liked_songs"]]:
            history["liked_songs"].append({
                "id": song["id"],
                "title": song["title"],
                "artist": song["artist"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Remove from disliked if it was there
        history["disliked_songs"] = [s for s in history["disliked_songs"] if s["id"] != song["id"]]
    
    elif action == "disliked":
        if song["id"] not in [s["id"] for s in history["disliked_songs"]]:
            history["disliked_songs"].append({
                "id": song["id"],
                "title": song["title"],
                "artist": song["artist"],
                "timestamp": datetime.now().isoformat()
            })
    
    elif action == "recommended":
        # Keep last 50 recommendations to avoid clutter
        history["recommended_songs"] = history["recommended_songs"][-50:]
        if song["id"] not in [s["id"] for s in history["recommended_songs"]]:
            history["recommended_songs"].append({
                "id": song["id"],
                "title": song["title"],
                "artist": song["artist"],
                "timestamp": datetime.now().isoformat()
            })
    
    save_user_history(user_id, history)

def get_excluded_songs(user_id: str) -> Set[str]:
    """Get IDs of songs that should be excluded from recommendations"""
    history = get_user_history(user_id)
    excluded = set()
    
    # Exclude recently disliked songs (last 20)
    for song in history["disliked_songs"][-20:]:
        excluded.add(song["id"])
    
    # Exclude recently recommended songs (last 10 to avoid immediate repeats)
    for song in history["recommended_songs"][-10:]:
        excluded.add(song["id"])
    
    return excluded