import json
from pathlib import Path
from typing import Any

from sklearn.metrics import accuracy_score
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression


def load_data() -> list[dict[str, Any]]:
    """
    Loads user interactions from data/interactions.json
    Each entry should include the song's genres and whether the user liked or disliked it.
    """
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "data" / "interactions.json"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def train_model() -> tuple[LogisticRegression | None, DictVectorizer | None]:
    """
    Trains a logistic regression model to predict whether a user will like a song based on its genres.
    Loads user interactions from data/interactions.json, vectorizes the genres, and fits the model
    """
    data = load_data()

    if not data:
        print("No data available for training. Please log some interactions first.")
        return None, None

    X = [{"genre": d["genre"]} for d in data]
    y = [d["liked"] for d in data]

    # Keep a dense matrix to avoid shape friction with small tabular inputs.
    vectorizer = DictVectorizer(sparse=False)
    X_vectorized = vectorizer.fit_transform(X)

    # Train a logistic regression model
    model = LogisticRegression()
    model.fit(X_vectorized, y)

    return model, vectorizer


def evaluate_model():
    """
    Evaluates the trained model on the same data (since we don't have a separate test set) and prints the accuracy.
    In a real application, you would want to use a separate test set or cross-validation.
    """
    model, vec = train_model()
    data = load_data()

    if model is None or vec is None:
        return

    X = [{"genre": d["genre"]} for d in data]
    y = [d["liked"] for d in data]

    X_features: Any = X
    X_vec = vec.transform(X_features)
    preds = model.predict(X_vec)

    acc = accuracy_score(y, preds)
    print(f"Model Accuracy: {acc:.2f}")