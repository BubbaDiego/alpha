import pytest

from data.data_locker import DataLocker
from calc_core.calculation_core import CalculationCore


@pytest.fixture
def dl(monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)
    locker = DataLocker(":memory:")
    yield locker
    locker.db.close()


def test_calculation_core_loads_modifiers_from_db(dl):
    dl.modifiers.set_modifier("distanceWeight", 0.9)
    dl.modifiers.set_modifier("leverageWeight", 0.8)
    dl.modifiers.set_modifier("collateralWeight", 0.7)

    calc = CalculationCore(dl)
    assert calc.modifiers == {
        "distanceWeight": 0.9,
        "leverageWeight": 0.8,
        "collateralWeight": 0.7,
    }
    assert calc.calc_services.weights == calc.modifiers
