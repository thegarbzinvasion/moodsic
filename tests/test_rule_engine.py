import pytest

from moodsic.rule_engine import get_bucket


def test_returns_expected_bucket_for_representative_values():
    assert get_bucket(10)["bucket"].startswith("A:")
    assert get_bucket(25)["bucket"].startswith("B:")
    assert get_bucket(50)["bucket"].startswith("C:")
    assert get_bucket(70)["bucket"].startswith("D:")
    assert get_bucket(90)["bucket"].startswith("E:")


def test_returns_expected_structure_and_genres_type():
    result = get_bucket(55)

    assert set(result.keys()) == {"bucket", "genres"}
    assert isinstance(result["bucket"], str)
    assert isinstance(result["genres"], list)
    assert all(isinstance(genre, str) for genre in result["genres"])
    assert len(result["genres"]) > 0


def test_boundaries_are_inclusive_at_min_and_max_limits():
    assert get_bucket(0)["bucket"].startswith("A:")
    assert get_bucket(20)["bucket"].startswith("B:")
    assert get_bucket(40)["bucket"].startswith("C:")
    assert get_bucket(60)["bucket"].startswith("D:")
    assert get_bucket(80)["bucket"].startswith("E:")
    assert get_bucket(100)["bucket"].startswith("E:")


def test_raises_type_error_for_non_numeric_values():
    with pytest.raises(TypeError):
        get_bucket("50")  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        get_bucket(None)  # type: ignore[arg-type]


def test_raises_value_error_outside_valid_range():
    with pytest.raises(ValueError):
        get_bucket(-0.01)

    with pytest.raises(ValueError):
        get_bucket(100.01)
