from moodsic.ml_model import train_model, evaluate_model
import json
from pathlib import Path

def retrain_if_needed(user_id: str):
    """Retrain model after 10 new interactions"""
    project_root = Path(__file__).resolve().parents[2]
    interactions_path = project_root / "data" / "interactions.json"
    
    with open(interactions_path, "r") as f:
        interactions = json.load(f)
    
    # Check if we've added significant new data
    if len(interactions) % 10 == 0 and len(interactions) > 0:
        print("Retraining model with new data...")
        train_model()
        evaluate_model()