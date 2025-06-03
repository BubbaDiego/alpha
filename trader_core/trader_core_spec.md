# 🧑‍💼 TraderCore Specification

> Version: `v1.0`
> Author: `CoreOps 🧠`
> Scope: Service layer for managing Trader creation, enrichment, and lifecycle operations

---

## 📂 Module Structure
```txt
trader_core/
├── trader_core.py            # 🌟 Central core logic for trader creation and updates
├── trader_factory_service.py # 🛠️ Optional builder for persona-to-trader conversion
├── trader_store.py           # 💾 Persistence and lookup utilities
```

## 🎯 Purpose
The TraderCore is responsible for:

- Creating new Trader entities based on persona configurations.
- Enriching trader data with live portfolio and position information.
- Managing mood, heat index, and performance scores.
- Persisting trader metadata in the database.
- Serving as the service gateway for factory UIs or API endpoints.

## 🧱 Constructor
```python
class TraderCore:
    def __init__(self, data_locker, persona_manager=None, strategy_manager=None)
```
- `data_locker`: Required. Used for accessing positions, portfolio, wallets.
- `persona_manager`: Optional override; otherwise loaded internally.
- `strategy_manager`: Optional override.

## 🛠 Key Methods
- `create_trader(trader_name: str) -> Trader`
  - Creates a Trader instance from a registered persona.
  - Loads persona profile.
  - Computes mood via `evaluate_mood(...)`.
  - Computes performance score.
  - Pulls positions, portfolio, and wallet data.
  - Returns a full Trader object (not persisted).
- `save_trader(trader: Trader) -> bool`
  - Persists a Trader's metadata.
  - Stores persona-specific overrides if applicable.
  - Saves to traders table (if it exists).
  - Future-proofed for tracking trader history or evolution.
- `get_trader(name: str) -> Trader`
  - Returns the enriched trader object using current data and persona config.
- `list_traders() -> List[Trader]`
  - Returns enriched traders for all available personas.
- `delete_trader(name: str) -> bool`
  - Optional. Deletes associated metadata (not personas or wallets).

## 🧠 Mood and Score Logic
Uses `mood_engine.evaluate_mood(heat_index, mood_map)` for:

- Assigning trader mood based on average heat index.
- Score formula (subject to tuning):

```python
score = int(100 - abs(avg_heat_index - 30))
```

## 📄 Trader Object
This module relies on the `Trader` data class:

```python
@dataclass
class Trader:
    name: str
    avatar: str
    persona: str
    origin_story: str
    risk_profile: str
    mood: str
    moods: Dict[str, str]
    strategies: Dict[str, float]
    wallet: str
    portfolio: Dict
    positions: List[Dict]
    hedges: List[Dict]
    performance_score: int
    heat_index: float
```

## 🔗 Integrations
Used by:
- `trader_bp.py` Flask routes (`/factory/<name>`, `/api/<name>`)
- Factory UI (HTML/JS) for trader creation and visualization

Depends on:
- `oracle_core.strategy_manager`
- `oracle_core.persona_manager`
- `oracle_core.oracle_data_service`
- `calc_core.calc_services`
- `mood_engine.evaluate_mood`

## 🔧 Future Expansion
- Trader lifecycle tracking (e.g. day-to-day score deltas)
- GPT analysis through `OracleCore.ask_trader(...)`
- Trader team generation (group trading simulations)
- Enhanced factory UI creation wizard
