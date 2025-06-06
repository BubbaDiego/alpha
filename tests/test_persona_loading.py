import importlib


def test_persona_manager_loads_bundle():
    pm_mod = importlib.import_module("oracle_core.persona_manager")
    manager = pm_mod.PersonaManager()
    for name in ("Connie", "Nina", "Angie", "Wizard"):
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


def test_trader_personas_load():
    pm_mod = importlib.import_module("oracle_core.persona_manager")
    manager = pm_mod.PersonaManager(base_dir="trader_core/personas")
    for name in ("Vader", "R2", "Yoda", "Lando", "Leia"):
        assert name in manager.list_personas()
