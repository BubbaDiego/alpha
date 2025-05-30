import pytest
from calc_core.calc_services import CalcServices

@pytest.fixture
def sample_position():
    return {
        "position_type": "LONG",
        "entry_price": 100.0,
        "liquidation_price": 50.0,
        # Size represents token amount. Entry price is 100, collateral is 100.
        # Value is calculated as collateral plus P&L.
        "size": 2.0,
        "collateral": 100.0,
        "leverage": 2.0,
    }

def test_price_metric_functions(sample_position):
    calc = CalcServices()
    price = 90.0
    assert calc.value_at_price(sample_position, price) == pytest.approx(99.8)
    assert calc.travel_percent_at_price(sample_position, price) == pytest.approx(-20.0)
    assert calc.liquid_distance_at_price(sample_position, price) == 40.0
    # Collateral is high relative to size so risk floor of 5 applies
    assert calc.heat_index_at_price(sample_position, price) == pytest.approx(5.0)

def test_evaluate_at_price(sample_position):
    calc = CalcServices()
    price = 120.0
    result = calc.evaluate_at_price(sample_position, price)
    assert result["value"] == pytest.approx(100.4)
    assert result["travel_percent"] == pytest.approx(40.0)
    assert result["liquidation_distance"] == 70.0
    assert result["heat_index"] == pytest.approx(5.0)

