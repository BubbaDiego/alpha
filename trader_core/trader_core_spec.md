# 🧠 Trader Core Specification

> Version: `v1.0`
> Author: `CoreOps 🧠`
> Scope: Build, persist, and manage Trader personas tied to portfolio strategy and mood evaluation.

---

## 📂 Module Structure
```txt
trader/
├── trader_core.py             # Main service logic
├── trader_store.py            # In-memory fallback store
├── trader_factory_service.py  # UI/console wrapper
├── trader_loader.py           # Legacy loader (read-only)
├── trader.py                  # Trader dataclass
├── mood_engine.py             # Heat-based mood selection
├── templates/trader_factory.html # UI panel
```

---

## 🧠 Purpose
The Trader module generates strategy-aware trader personas from live portfolio data, based on:
- Persona configuration
- Strategy weights
- Risk & heat index metrics

It serves:
- Console workflows
- GPT query context
- UI previews + saving to DB

---
 
## ⚙️ `TraderCore`

### Constructor
```python
TraderCore(data_locker, persona_manager=None, strategy_manager=None)
```

### Key Methods
| Method                | Description |
|-----------------------|-------------|
| `create_trader(name)` | Generate Trader object with live metrics |
| `save_trader(t)`      | Save to DB or fallback to memory |
| `get_trader(name)`    | Load trader, fall back to create + cache |
| `list_traders()`      | List all persisted or persona-based traders |
| `delete_trader(name)` | Remove from DL or memory store |

---

## 📋 Trader Dataclass
```python
@dataclass
class Trader:
    name: str
    avatar: str = ""
    persona: str = ""
    origin_story: str = ""
    risk_profile: str = ""
    mood: str = "neutral"
    moods: Dict[str, str] = field(default_factory=dict)
    strategies: Dict[str, float] = field(default_factory=dict)
    wallet: str = ""
    portfolio: Dict = field(default_factory=dict)
    positions: List[Dict] = field(default_factory=list)
    hedges: List[Dict] = field(default_factory=list)
    performance_score: int = 0
    heat_index: float = 0.0
    created_at: str = now()
    last_updated: str = now()
```

---

## 🛢️ Persistence

### 🔘 In-Memory Store
Used for dev testing (`TraderStore`)

### 💾 DL Trader Store (`DLTraderManager`)
- Table: `traders`
- Fields:
  - `name TEXT PRIMARY KEY`
  - `trader_json TEXT NOT NULL[trader_bp.py](trader_bp.py)`
  - `created_at TEXT`
  - `last_updated TEXT`
- JSON-encodes entire object

---


## 🎨 UI (HTML)
- Dropdown persona selector
- Preview panel (`<pre>`)
- Save + delete buttons
- Real-time sync with backend
- Optional Oracle button
- Leaderboard and activity log

---

---

## 🔮 GPT Integration
`OracleCore.ask_trader()` uses Trader object to:
- Merge persona strategy modifiers
- Add context from trader.portfolio + positions
- Inject mood

---

## ✅ Summary
TraderCore makes GPT-guided trader personas actionable.
It enables strategy tuning, UI simulation, logging, and full DB lifecycle management.
Perfect for simulation dashboards, GPT context delivery, and user-driven portfolios.

---
