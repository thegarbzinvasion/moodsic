from decimal import Decimal, ROUND_HALF_UP

COLOR_TO_VALUE = {
    "red": Decimal("1.0"),
    "blue": Decimal("2.0"),
    "purple": Decimal("3.0"),
    "yellow": Decimal("5.5"),
    "green": Decimal("7.0"),
}

MULTIPLIER = Decimal("3.57")

def calculate_mood_percentage(q1: int, q2: int, q3: int, color: str) -> float:
    """
    Returns mood percetage based on spec.md.
    """

    if not isinstance(q1, int) or not isinstance(q2, int) or not isinstance(q3, int):
        raise TypeError("q1, q2, and q3 must be integers.")
    if not isinstance(color, str):
        raise TypeError("color must be a string.")

    if not (q1 >= 1 and q1 <= 7):
        raise ValueError(f"q1 must be between 1 and 7, got {q1}")
    if not (q2 >= 1 and q2 <= 7):
        raise ValueError(f"q2 must be between 1 and 7, got {q2}")
    if not (q3 >= 1 and q3 <= 7):
        raise ValueError(f"q3 must be between 1 and 7, got {q3}")
    
    if color not in COLOR_TO_VALUE:
        raise ValueError(f"color must be one of {list(COLOR_TO_VALUE.keys())}, got {color}")
    
    mood_raw = Decimal(str(q1)) + Decimal(str(q2)) + Decimal(str(q3)) + COLOR_TO_VALUE[color]
    mood_pct = mood_raw * MULTIPLIER    

    # 2dp rounding with "half up" so 41.055 -> 41.06

    mood_pct = mood_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return float(mood_pct)