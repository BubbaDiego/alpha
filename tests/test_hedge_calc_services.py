import pytest

from hedge_core.hedge_calc_services import HedgeCalcServices


def test_evaluate_at_price_basic():
    long_pos = {
        "position_type": "LONG",
        "entry_price": 100.0,
        "size": 1000.0,
        "collateral": 500.0,
    }
    short_pos = {
        "position_type": "SHORT",
        "entry_price": 110.0,
        "size": 1000.0,
        "collateral": 500.0,
    }
    calc = HedgeCalcServices()
    result = calc.evaluate_at_price(long_pos, short_pos, 105.0)

    assert pytest.approx(result["long"]["pnl"], rel=1e-6) == 50.0
    assert pytest.approx(result["short"]["pnl"], rel=1e-6) == 45.454545
    assert pytest.approx(result["net"]["pnl"], rel=1e-6) == 95.454545
    assert pytest.approx(result["net"]["imbalance"], rel=1e-6) == 4.545455


def test_suggest_rebalance_equal_value_collateral():
    long_pos = {
        "position_type": "LONG",
        "entry_price": 100.0,
        "size": 1000.0,
        "collateral": 500.0,
    }
    short_pos = {
        "position_type": "SHORT",
        "entry_price": 110.0,
        "size": 1000.0,
        "collateral": 500.0,
    }
    calc = HedgeCalcServices()
    config = {
        "adjustment_target": "equal_value",
        "adjustable_side": "long",
        "adjust_fields": ["collateral"],
    }
    suggestion = calc.suggest_rebalance(long_pos, short_pos, 105.0, config)

    expected_collateral = 495.454545  # reduce by imbalance
    assert suggestion["side"] == "long"
    assert pytest.approx(suggestion["updates"]["collateral"], rel=1e-6) == expected_collateral

