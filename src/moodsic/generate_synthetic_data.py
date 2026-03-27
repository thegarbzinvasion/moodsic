"""
Generate synthetic interactions data from bucket genres.
Creates realistic user feedback patterns to improve ML model training.
"""

import json
import random
from pathlib import Path
from typing import Any

# All genres from rule_engine buckets
BUCKET_GENRES = {
    "A": ["slowcore", "drone", "dark-ambient", "neoclssical-darkwave", "chamber-folk"],
    "B": ["neo-psychedelia", "chamber-pop", "dream-pop", "shoegaze", "conscious hip-hop"],
    "C": ["baroque-pop", "trap-soul", "orchestral", "contemporary-r&b", "alternative-r&b"],
    "D": ["trap", "electronic", "industrial metal", "nu jazz", "experimental hip-hop", "art-pop", "alt-pop"],
    "E": ["pop-rap", "digicore", "hyperpop", "future-bass", "deconstructed club", "bubblegum bass", "jazz-rap", "dance-pop"],
}

def generate_interactions(num_interactions: int = 1000) -> list[dict[str, Any]]:
    """
    Generate synthetic interactions with realistic like/dislike patterns.
    
    Assumptions:
    - Users tend to like genres from their current mood bucket
    - Users dislike genres from far-away mood buckets
    - Some cross-bucket likes/dislikes for realism
    """
    interactions = []
    bucket_order = ["A", "B", "C", "D", "E"]
    
    # Generate interactions proportionally from each bucket
    interactions_per_bucket = num_interactions // len(bucket_order)
    
    for bucket_idx, bucket in enumerate(bucket_order):
        genres = BUCKET_GENRES[bucket]
        
        for _ in range(interactions_per_bucket):
            # Pick a genre from this bucket (80% of the time)
            if random.random() < 0.8:
                genre = random.choice(genres)
            else:
                # Sometimes pick from adjacent bucket for realism
                adjacent_bucket = random.choice([b for i, b in enumerate(bucket_order) if abs(i - bucket_idx) == 1])
                genre = random.choice(BUCKET_GENRES[adjacent_bucket])
            
            # Like probability: higher for genres in their bucket
            if genre in genres:
                # 70% like genres from their bucket
                liked = random.random() < 0.7
            else:
                # 40% like genres from other buckets
                liked = random.random() < 0.4
            
            interactions.append({
                "genre": genre,
                "liked": 1 if liked else 0
            })
    
    # Shuffle for realism
    random.shuffle(interactions)
    
    return interactions


def save_synthetic_data(interactions: list[dict[str, Any]]) -> None:
    """Save interactions to data/interactions.json"""
    project_root = Path(__file__).resolve().parents[2]
    interactions_path = project_root / "data" / "interactions.json"
    
    with open(interactions_path, "w", encoding="utf-8") as f:
        json.dump(interactions, f, indent=2)
    
    print(f"✓ Generated {len(interactions)} interactions")
    print(f"✓ Saved to {interactions_path}")
    
    # Print stats
    likes = sum(1 for i in interactions if i["liked"] == 1)
    dislikes = len(interactions) - likes
    print(f"✓ Likes: {likes} ({100*likes/len(interactions):.1f}%)")
    print(f"✓ Dislikes: {dislikes} ({100*dislikes/len(interactions):.1f}%)")
    
    # Print genre distribution
    genre_counts = {}
    for interaction in interactions:
        genre = interaction["genre"]
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    print("\n✓ Genre distribution:")
    for bucket in ["A", "B", "C", "D", "E"]:
        bucket_genres = BUCKET_GENRES[bucket]
        bucket_total = sum(genre_counts.get(g, 0) for g in bucket_genres)
        print(f"  {bucket}: {bucket_total} ({100*bucket_total/len(interactions):.1f}%)")


if __name__ == "__main__":
    # Generate and save 1000 synthetic interactions
    print("Generating 1000 synthetic interactions...")
    interactions = generate_interactions(1000)
    save_synthetic_data(interactions)
    print("\n✓ Done! Run `python evalulate.py` to test the model with more data.")
