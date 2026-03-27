from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
	sys.path.insert(0, str(SRC_PATH))

from moodsic.ml_model import evaluate_model_comprehensive

evaluate_model_comprehensive()