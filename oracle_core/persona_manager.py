import json
import os

from typing import Dict, Iterable, Optional



class Persona:
    """Simple persona container."""

    def __init__(self, data: Dict):
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.modifiers = data.get("modifiers", {})
        self.strategy_weights = data.get("strategy_weights", {})
        self.instructions = data.get("instructions", "")

        self.system_message = data.get("system_message", "")



class PersonaManager:
    """Load and manage personas."""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = base_dir
            self.extra_dirs: Iterable[str] = []
        else:
            self.base_dir = os.path.join(os.path.dirname(__file__), "personas")
            self.extra_dirs = [
                os.path.join(os.path.dirname(__file__), "..", "trader_core", "personas")
            ]
        self._personas: Dict[str, Persona] = {}
        self._load_all()

    def _load_all(self):
        dirs = [self.base_dir] + list(getattr(self, "extra_dirs", []))
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fname in os.listdir(d):
                if fname.endswith(".json"):
                    self.load_from_file(os.path.join(d, fname))

    def load(self, personas: Iterable[Dict]):
        for data in personas:
            self.register(data)


    def load_from_file(self, path: str):
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        if isinstance(data, dict) and "name" in data:
            self.register(data)
        elif isinstance(data, list):
            self.load(data)

    def register(self, data: Dict):
        persona = data if isinstance(data, Persona) else Persona(data)
        self._personas[persona.name] = persona

    def get(self, name: str) -> Persona:

        return self._personas[name]

    def list_personas(self) -> Iterable[str]:
        return list(self._personas.keys())

    def merge_modifiers(self, base: Dict[str, float], persona_name: str) -> Dict[str, float]:
        persona = self.get(persona_name)
        merged = dict(base)
        merged.update(persona.modifiers)
        return merged

