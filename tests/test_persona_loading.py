import importlib


def test_persona_manager_loads_bundle():
    pm_mod = importlib.import_module("oracle_core.persona_manager")
    manager = pm_mod.PersonaManager()
    for name in ("Selena", "Nina", "Angie", "Wizard"):
        assert name in manager.list_personas()


def test_persona_strategy_weights():
    pm_mod = importlib.import_module("oracle_core.persona_manager")
    manager = pm_mod.PersonaManager()
    persona = manager.get("Wizard")
    assert persona.strategy_weights == {
        "dynamic_hedging": 0.9,
        "profit_management": 0.1,
    }


def test_persona_attributes_loaded():
    pm_mod = importlib.import_module("oracle_core.persona_manager")
    manager = pm_mod.PersonaManager()
    persona = manager.get("risk_averse")
    assert persona.strategy_weights == {"safe": 0.7, "cautious": 0.3}
    assert persona.instructions == "Adopt a conservative trading approach."
    assert hasattr(persona, "system_message")
