BUCKETS = [
    {
        "name": "A: Total mental and physical exhaustion (0-19)",
        "min": 0.0,
        "max": 20.0,
        "genres": [
            "slowcore",
            "drone",
            "dark-ambient",
            "neoclssical-darkwave",
            "chamber-folk"
        ],
    },

    {
        "name": "B: Drained / burnout risk (20-39)",
        "min": 20.0,
        "max": 40.0,
        "genres": [
            "neo-psychedelia",
            "chamber-pop",
            "dream-pop",
            "shoegaze",
            "conscious hip-hop",        
        ],
    },

    {
        "name": "C: Neutral but no safety net (40-59)",
        "min": 40.0,
        "max": 60.0,
        "genres": [
            "baroque-pop",
            "trap-soul",
            "orchestral",
            "contemporary-r&b",
            "alternative-r&b",
        ],
    },

    {
        "name": "D: Doing well but something's going on (60-84)",
        "min": 60.0,
        "max": 80.0,
        "genres": [
            "trap",
            "electronic",
            "industrial metal",
            "nu jazz",
            "experimental hip-hop",
            "art-pop",
            "alt-pop",
        ],
    },

    {
        "name": "E: High energy and low noise in the head (85-100)", 
        "min": 80.0,
        "max": 100.0,
        "genres": [
            "pop-rap",
            "digicore",
            "hyperpop",
            "future-bass",
            "deconstructed club",
            "bubblegum bass",
            "jazz-rap",
            "dance-pop",      
        ],
    }
]

# Test each bucket in separate test file also for type and value error
def get_bucket(mood_percentage: float) -> dict:
    """
    Returns a dict: { "bucket": <bucket name>, "genres": [<genre strings>] }
    Boundaries follow spec:
      - A: 0 <= pct < 20
      - B: 20 <= pct < 40
      - C: 40 <= pct < 60
      - D: 60 <= pct < 85
      - E: 85 <= pct <= 100
    """
    if not isinstance(mood_percentage, (int, float)):
        raise TypeError("mood_percentage must be a number.")
    
    mood_percentage = float(mood_percentage)
    if mood_percentage < 0.0 or mood_percentage > 100.0:
        raise ValueError(f"mood_percentage must be between 0 and 100, got {mood_percentage}")   

    for bucket in BUCKETS:
        # All buckets except the last are: min <= mood_percentage < max

        if bucket["name"].startswith("A:"):
            # First bucket is: 0 <= mood_percentage < 20
            if mood_percentage >= bucket["min"] and mood_percentage < bucket["max"]:
                return {"bucket": bucket["name"], "genres": bucket["genres"]}
        elif bucket["name"].startswith("B:"):
            # Second bucket is: 20 <= mood_percentage < 40
            if mood_percentage >= bucket["min"] and mood_percentage < bucket["max"]:
                return {"bucket": bucket["name"], "genres": bucket["genres"]}
        elif bucket["name"].startswith("C:"):
            # Third bucket is: 40 <= mood_percentage < 60
            if mood_percentage >= bucket["min"] and mood_percentage < bucket["max"]:
                return {"bucket": bucket["name"], "genres": bucket["genres"]}
        elif bucket["name"].startswith("D:"):
            # Fourth bucket is: 60 <= mood_percentage < 85
            if mood_percentage >= bucket["min"] and mood_percentage < bucket["max"]:
                return {"bucket": bucket["name"], "genres": bucket["genres"]}
        elif bucket["name"].startswith("E:"):
            # Last bucket is: 85 <= mood_percentage <= 100
            if mood_percentage >= bucket["min"] and mood_percentage <= bucket["max"]:
                return {"bucket": bucket["name"], "genres": bucket["genres"]}
        else:
            if mood_percentage >= bucket["min"] and mood_percentage < bucket["max"]:
                return {"bucket": bucket["name"], "genres": bucket["genres"]}
            
    raise RuntimeError("No bucket matched. Check bucket definitions.")