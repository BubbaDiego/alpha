import math
from utils.alert_helpers import calculate_threshold_progress


def test_progress_basic():
    assert math.isclose(calculate_threshold_progress(100, 110, 105), 50)


def test_progress_start_none():
    assert math.isclose(calculate_threshold_progress(None, 10, 5), 50)


def test_progress_start_equal_trigger():
    assert math.isclose(calculate_threshold_progress(10, 10, 15), 100)


def test_progress_trigger_zero():
    assert calculate_threshold_progress(None, 0, 5) == 0
