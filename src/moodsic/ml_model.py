import json
from pathlib import Path
from typing import Any

from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import cross_val_score
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
    Legacy evaluation function. Use evaluate_model_comprehensive() instead.
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

def evaluate_model_comprehensive():
    """
    Comprehensive evaluation with cross-validation, precision, recall, and F1.
    Tier 1 metrics for Moodsic:
    - Train-on-all accuracy (for reference)
    - Precision, Recall, F1 (for recommendation quality)
    - 5-fold cross-validation score (for generalization)
    """
    data = load_data()

    if not data:
        print("No data available for evaluation.")
        return

    X = [{"genre": d["genre"]} for d in data]
    y = [d["liked"] for d in data]

    # Vectorize
    vectorizer = DictVectorizer(sparse=False)
    X_vec = vectorizer.fit_transform(X)

    # Train model and evaluate on same data
    model = LogisticRegression()
    model.fit(X_vec, y)
    preds = model.predict(X_vec)

    # Compute accuracy
    acc = accuracy_score(y, preds)

    # Compute precision, recall, F1 (weighted for class imbalance)
    precision, recall, f1, support = precision_recall_fscore_support(
        y, preds, average="weighted", zero_division=0
    )

    # 5-fold cross-validation
    cv_scores = cross_val_score(model, X_vec, y, cv=5, scoring="f1_weighted")
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()

    # Print comprehensive report
    print("\n" + "=" * 50)
    print("ML MODEL EVALUATION REPORT")
    print("=" * 50)
    print(f"\nDataset: {len(data)} interactions")
    print(f"Classes (Liked/Disliked): {sum(y)} / {len(y) - sum(y)}")
    print("\n--- Train-on-All Performance (Reference) ---")
    print(f"Accuracy:  {acc:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1-Score:  {f1:.3f}")
    print("\n--- 5-Fold Cross-Validation ---")
    print(f"CV Mean F1: {cv_mean:.3f}")
    print(f"CV Std:     {cv_std:.3f}")
    print(f"Individual fold scores: {[f'{s:.3f}' for s in cv_scores]}")
    print("\n" + "=" * 50)
    print("\nInterpretation:")
    print("- If CV Mean is much lower than Train Accuracy: model may overfit")
    print("- Higher F1 is better for imbalanced recommendation tasks")
    print("- CV Std shows stability across different data splits")
    print("=" * 50 + "\n")