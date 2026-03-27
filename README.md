# Moodsic

Moodsic is a mood-based music recommender that combines:

- rule-based mood bucketing
- user preference learning from likes and skips
- a lightweight ML model that learns genre preference patterns
- Last.fm recommendations with local fallback data

You can use it through a Streamlit app or a CLI flow.

## Features

- Mood check-in with 3 sliders + color association
- Mood percentage and bucket assignment
- Genre selection from rule buckets
- Song recommendations from Last.fm first, local sample data as fallback
- Per-song feedback loop (Like or Skip)
- Interaction logging to improve recommendations over time
- ML-assisted scoring with logistic regression

## Project Structure

```text
moodsic/
	app.py                         # Streamlit UI
	main.py                        # CLI app
	evalulate.py                   # ML model evaluation script
	src/moodsic/
		mood_calculator.py           # Mood percentage logic
		rule_engine.py               # Bucket and genre mapping
		recommender.py               # Recommendation pipeline
		ml_model.py                  # Train and evaluate model
		lastfm_client.py             # Last.fm integration
		retrain.py                   # Retrain trigger helper
		user_history.py              # Per-user history handling
	data/
		songs.sample.json            # Local fallback songs
		users.sample.json            # User genre preferences
		interactions.json            # Feedback interaction log
		user_1_history.json          # User history snapshot
	tests/
		test_mood_calculator.py
		test_rule_engine.py
```

## Requirements

- Python 3.11+ (your current project also runs in 3.14)
- pip
- Optional: Last.fm API credentials for online recommendations

Main Python packages used:

- streamlit
- python-dotenv
- scikit-learn
- pylast
- pytest

## Setup

1. Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install streamlit python-dotenv scikit-learn pylast pytest
```

3. Create a .env file in the project root.

```env
LASTFM_API_KEY=your_key_here
LASTFM_SHARED_SECRET=your_shared_secret_here
```

If .env is missing or credentials are invalid, the app still works with local fallback recommendations.

## Run The App

```powershell
python -m streamlit run app.py
```

Streamlit usually opens at:

- http://localhost:8501

## Run CLI Mode

```powershell
python main.py
```

## Check ML Model Health

Run evaluation:

```powershell
python evalulate.py
```

Expected output format:

```text
Model Accuracy: 0.xx
```

## Retraining

The helper in src/moodsic/retrain.py retrains when interaction count reaches each multiple of 10.

Example usage:

```python
from moodsic.retrain import retrain_if_needed

retrain_if_needed("user_1")
```

## Testing

```powershell
pytest -q
```

Current tests cover mood calculation and rule bucket logic. If you expand ML behavior, add tests for ml_model.py and recommender ranking.

## Data Notes

- data/interactions.json grows over time as feedback is logged.
- data/users.sample.json stores learned liked and disliked genres.
- data/user_1_history.json stores recommendation and feedback history.

## Troubleshooting

- Streamlit command not found:
	- Use python -m streamlit run app.py
- No Last.fm songs returned:
	- Check .env credentials
	- App should still fill with local fallback songs
- Empty or weak ML signal:
	- Add more feedback interactions and rerun evalulate.py

## Roadmap Ideas

- Add a proper dependency file (requirements.txt or pyproject.toml)
- Add dedicated tests for ml_model.py and lastfm_client.py
- Add model persistence and train or test split evaluation
- Add multi-user login and profile-level personalization