import pytest

from moodsic.mood_calculator import calculate_mood_percentage

# Behaviors covered:
# 1) Computes correct percentage for valid inputs
# 2) Rounds result to 2 decimal places
# 3) Validates q1/q2/q3 are between 1 and 7 inclusive (below range raises)
# 4) Validates q1/q2/q3 are between 1 and 7 inclusive (above range raises)
# 5) Validates color is in allowed set (invalid color raises)
# 6) Color matching is case-sensitive (e.g., "Red" invalid)
# 7) Non-integer questionnaire answers raise due to type comparison
# 8) Boundary values at extremes compute expected results

def test_computes_correct_percentage_valid_inputs():
    # q1=3, q2=4, q3=5, color=green(7.0)
    # raw = 3 + 4 + 5 + 7.0 = 19.0
    # pct = 19.0 * 3.57 = 67.83 -> round to 67.83
    assert calculate_mood_percentage(3, 4, 5, "green") == 67.83


def test_rounds_result_to_two_decimals():
    # q1=1, q2=2, q3=3, color=yellow(5.5)
    # raw = 11.5; pct = 41.055 -> 41.06 after rounding to 2dp
    assert calculate_mood_percentage(1, 2, 3, "yellow") == 41.06


def test_raises_when_any_question_below_minimum():
    with pytest.raises(ValueError):
        calculate_mood_percentage(0, 3, 3, "red")
    with pytest.raises(ValueError):
        calculate_mood_percentage(3, 0, 3, "red")
    with pytest.raises(ValueError):
        calculate_mood_percentage(3, 3, 0, "red")


def test_raises_when_any_question_above_maximum():
    with pytest.raises(ValueError):
        calculate_mood_percentage(8, 3, 3, "blue")
    with pytest.raises(ValueError):
        calculate_mood_percentage(3, 8, 3, "blue")
    with pytest.raises(ValueError):
        calculate_mood_percentage(3, 3, 8, "blue")


def test_raises_on_invalid_color():
    with pytest.raises(ValueError):
        calculate_mood_percentage(3, 3, 3, "orange")


def test_color_is_case_sensitive():
    # "Red" is not the same as "red"
    with pytest.raises(ValueError):
        calculate_mood_percentage(3, 3, 3, "Red")


def test_non_integer_answers_raise_type_error():
    # Using non-integers will trigger TypeError due to comparison operations
    with pytest.raises(TypeError):
        calculate_mood_percentage(3.5, 3, 3, "red")
    with pytest.raises(TypeError):
        calculate_mood_percentage("3", 3, 3, "red")  # type: ignore[arg-type]


def test_extreme_boundaries_compute_expected_values():
    # Minimum boundary: q1=q2=q3=1, color=red(1.0)
    # raw = 1 + 1 + 1 + 1.0 = 4.0; pct = 14.28
    assert calculate_mood_percentage(1, 1, 1, "red") == 14.28

    # Maximum boundary: q1=q2=q3=7, color=purple(3.0)
    # raw = 7 + 7 + 7 + 3.0 = 24.0; pct = 85.68
    assert calculate_mood_percentage(7, 7, 7, "purple") == 85.68
