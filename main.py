from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
	sys.path.insert(0, str(SRC_PATH))

from moodsic.mood_calculator import COLOR_TO_VALUE, calculate_mood_percentage
from moodsic.rule_engine import get_bucket
from moodsic.recommender import recommend_songs_for_genres

def _prompt_scale_value(label: str) -> int:
	while True:
		raw = input(f"{label} (1-7): ").strip()
		try:
			value = int(raw)
		except ValueError:
			print("Please enter a whole number between 1 and 7.")
			continue

		if 1 <= value <= 7:
			return value

		print("Value must be between 1 and 7.")

def _prompt_color() -> str:
	valid_colors = list(COLOR_TO_VALUE.keys())
	options = ", ".join(valid_colors)

	while True:
		color = input(f"Color ({options}): ").strip().lower()
		if color in COLOR_TO_VALUE:
			return color
		print(f"Please choose one of: {options}")

def main() -> None:
	print("Moodsic Check-In")
	print("Answer a few quick prompts to get your current mood bucket and genres.")

	q1 = _prompt_scale_value("Q1 Battery level")
	q2 = _prompt_scale_value("Q2 Internal monologue loudness")
	q3 = _prompt_scale_value("Q3 Buffer before hitting limit")
	color = _prompt_color()

	mood_pct = calculate_mood_percentage(q1=q1, q2=q2, q3=q3, color=color)
	bucket_result = get_bucket(mood_pct)

	print("\nResults")
	print(f"Mood % (2dp): {mood_pct:.2f}")
	print(f"Mood % (rounded): {round(mood_pct)}")
	print(f"Bucket: {bucket_result['bucket']}")

	print("\nRecommended Songs:")
	songs = recommend_songs_for_genres(bucket_result["genres"]) 

	for song in songs:
		print(f"- {song['title']} - {song['artist']}")


if __name__ == "__main__":
	main()
