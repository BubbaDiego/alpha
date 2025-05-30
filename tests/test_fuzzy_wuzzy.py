# tests/test_fuzzy_wuzzy.py

import pytest
from enum import Enum
from utils.fuzzy_wuzzy import fuzzy_match_enum, fuzzy_match_key


class AlertTypeStub(Enum):
    HeatIndex = "HeatIndex"
    Profit = "Profit"
    TravelPercentLiquid = "TravelPercentLiquid"


@pytest.mark.parametrize("input_str,expected", [
    ("Profit", AlertTypeStub.Profit),
    ("heatindex", AlertTypeStub.HeatIndex),
    ("travel-liquid", AlertTypeStub.TravelPercentLiquid),
])
def test_enum_fuzzy_match_success(input_str, expected):
    result = fuzzy_match_enum(input_str, AlertTypeStub)
    assert result == expected


def test_enum_fuzzy_match_with_alias():
    aliases = {
        "TravelPercentLiquid": ["travel", "liquid"]
    }
    result = fuzzy_match_enum("liquid", AlertTypeStub, aliases=aliases)
    assert result == AlertTypeStub.TravelPercentLiquid


def test_enum_fuzzy_match_fail_on_low_score():
    result = fuzzy_match_enum("asdfgh", AlertTypeStub, threshold=90.0)
    assert result is None


@pytest.mark.parametrize("input_str,expected", [
    ("avg_leverage", "avg_leverage"),
    ("average leverage", "avg_leverage"),
])
def test_key_fuzzy_match_success(input_str, expected):
    key_dict = {"avg_leverage": 1}
    result = fuzzy_match_key(input_str, key_dict)
    assert result == expected


def test_key_fuzzy_match_with_alias():
    key_dict = {"value_to_collateral_ratio": 1}
    aliases = {
        "value_to_collateral_ratio": ["vcr", "ratio"]
    }
    result = fuzzy_match_key("vcr", key_dict, aliases=aliases)
    assert result == "value_to_collateral_ratio"


def test_key_fuzzy_match_fail_on_low_score():
    key_dict = {"avg_leverage": 1}
    result = fuzzy_match_key("randomjunk", key_dict, threshold=90.0)
    assert result is None
