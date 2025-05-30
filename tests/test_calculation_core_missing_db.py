import pytest
from calc_core.calculation_core import CalculationCore
from calc_core.calc_services import CalcServices

class DummyDB:
    def get_cursor(self):
        return None

class DummyLocker:
    def __init__(self):
        self.db = DummyDB()


def test_load_modifiers_fallbacks_to_defaults():
    calc = CalculationCore(DummyLocker())
    assert calc.modifiers == CalcServices().weights
