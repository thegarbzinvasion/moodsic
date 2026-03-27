"""
Generate and expand songs.sample.json with 1000+ synthetic songs.
Uses all bucket genres and realistic artist/title combinations.
"""

import json
from pathlib import Path
import random

# All genres from buckets
BUCKET_GENRES = {
    "A": ["slowcore", "drone", "dark-ambient", "neoclssical-darkwave", "chamber-folk"],
    "B": ["neo-psychedelia", "chamber-pop", "dream-pop", "shoegaze", "conscious hip-hop"],
    "C": ["baroque-pop", "trap-soul", "orchestral", "contemporary-r&b", "alternative-r&b"],
    "D": ["trap", "electronic", "industrial metal", "nu jazz", "experimental hip-hop", "art-pop", "alt-pop"],
    "E": ["pop-rap", "digicore", "hyperpop", "future-bass", "deconstructed club", "bubblegum bass", "jazz-rap", "dance-pop"],
}

# Sample words for realistic-sounding artist names
ARTIST_PREFIXES = [
    "The", "Electric", "Synthetic", "Deep", "Lost", "Neon", "Crystal", "Void",
    "Aurora", "Nocturne", "Ephemeral", "Whispered", "Digital", "Ethereal",
]

ARTIST_SUFFIXES = [
    "Symphony", "Collective", "Project", "System", "Ensemble", "Experiment",
    "Theory", "Model", "State", "Echo", "Signal", "Pulse", "Static", "Flux",
]

# Sample song title words
SONG_TITLE_WORDS = [
    "Echoes", "Drift", "Fade", "Rise", "Fall", "Beyond", "Within", "Between",
    "Lost", "Found", "Silent", "Loud", "Bright", "Dark", "Cold", "Warm",
    "Distance", "Closure", "Beginning", "End", "Memory", "Dream", "Reality",
    "Whisper", "Cry", "Song", "Prayer", "Thought", "Feeling", "Time", "Space",
]

def generate_songs(num_songs: int = 1000) -> list[dict]:
    """Generate synthetic songs with bucket genres."""
    all_genres = []
    for bucket_genres in BUCKET_GENRES.values():
        all_genres.extend(bucket_genres)
    
    all_genres = list(set(all_genres))  # Deduplicate
    
    songs = []
    
    for i in range(num_songs):
        # Generate realistic artist name
        if random.random() < 0.5:
            artist = f"{random.choice(ARTIST_PREFIXES)} {random.choice(ARTIST_SUFFIXES)}"
        else:
            artist = f"{random.choice(ARTIST_SUFFIXES)} {random.choice(ARTIST_PREFIXES)}"
        
        # Generate realistic song title
        num_words = random.randint(1, 4)
        title = " ".join(random.sample(SONG_TITLE_WORDS, min(num_words, len(SONG_TITLE_WORDS))))
        
        # Pick 1-2 genres, biased toward single genre for simplicity
        if random.random() < 0.7:
            genres = [random.choice(all_genres)]
        else:
            genres = random.sample(all_genres, 2)
        
        songs.append({
            "id": i + 1,
            "title": title,
            "artist": artist,
            "genres": genres,
        })
    
    return songs


def expand_songs_json(num_new_songs: int = 1000) -> None:
    """Load existing songs.sample.json, add new songs, and save."""
    project_root = Path(__file__).resolve().parents[2]
    songs_path = project_root / "data" / "songs.sample.json"
    
    # Load existing songs
    with open(songs_path, "r", encoding="utf-8") as f:
        existing_songs = json.load(f)
    
    print(f"✓ Loaded {len(existing_songs)} existing songs")
    
    # Get max ID to continue numbering
    max_id = max(s["id"] for s in existing_songs)
    
    # Generate new songs
    new_songs = generate_songs(num_new_songs)
    
    # Renumber new songs to continue from existing
    for i, song in enumerate(new_songs):
        song["id"] = max_id + i + 1
    
    # Combine
    combined = existing_songs + new_songs
    
    # Save
    with open(songs_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)
    
    print(f"✓ Generated {len(new_songs)} new songs")
    print(f"✓ Total songs: {len(combined)}")
    print(f"✓ Saved to {songs_path}")
    
    # Print genre distribution
    genre_counts = {}
    for song in combined:
        for genre in song["genres"]:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    print("\n✓ Top 10 genres by frequency:")
    for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {genre}: {count} songs")


if __name__ == "__main__":
    import sys
    num_songs = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    print(f"Expanding songs.sample.json with {num_songs} new songs...")
    expand_songs_json(num_songs)
    print("\n✓ Done! Your recommender now has much more fallback content.")
