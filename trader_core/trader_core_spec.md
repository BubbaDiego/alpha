# 🔮 Oracle Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Strategy-aware topic aggregator for GPT queries.

---

## 📂 Module Structure
```txt
oracle_core/
├── oracle_core.py           # Main orchestrator
├── oracle_data_service.py   # Fetch context data from DataLocker
├── strategy_manager.py      # Load strategy definitions
├── persona_manager.py       # Load persona definitions
├── alerts_topic_handler.py  # Build alerts context
├── portfolio_topic_handler.py   # Build portfolio context
├── positions_topic_handler.py   # Build positions context
├── prices_topic_handler.py      # Build price context
├── system_topic_handler.py      # Build system status context
├── personas/                # Default persona JSON files
└── strategies/              # Strategy modifier JSON files
```

### 🔮 `OracleCore`
Central entry point that builds prompts and invokes the OpenAI API.

```python
class OracleCore:
    def __init__(self, data_locker):
        self.data_locker = data_locker
        if OpenAI:
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY") or ""
            self.client = OpenAI(api_key=api_key) if api_key else None
        else:
            self.client = None
        self.strategy_manager = StrategyManager()
        self.persona_manager = PersonaManager()
        self.handlers: Dict[str, object] = {}
        self.register_topic_handler("portfolio", PortfolioTopicHandler(data_locker))
        self.register_topic_handler("alerts", AlertsTopicHandler(data_locker))
        self.register_topic_handler("prices", PricesTopicHandler(data_locker))
        self.register_topic_handler("system", SystemTopicHandler(data_locker))
        self.register_topic_handler("positions", PositionsTopicHandler(data_locker))
```
【F:oracle_core/oracle_core.py†L16-L38】

`ask()` obtains context from the selected handler and optionally applies a strategy or persona before sending the prompt to GPT.

### 🎭 Personas and Strategies
`PersonaManager` loads persona JSON files that provide instructions and strategy weights. `StrategyManager` loads strategy JSON files defining modifier dictionaries. Persona weights are merged so multiple strategies can influence the final prompt.

### 🗂️ Topic Handlers
Each handler (`PortfolioTopicHandler`, `PositionsTopicHandler`, `AlertsTopicHandler`, `PricesTopicHandler`, `SystemTopicHandler`) returns a small context dictionary via `OracleDataService`.
The positions context now returns both the list of positions and an `avg_heat_index` field used by the `heat_control` strategy.

### 🛰️ Data Service
`OracleDataService` wraps `DataLocker` managers and exposes helpers:
- `fetch_portfolio()` → latest portfolio snapshot
- `fetch_alerts()` → recent alerts
- `fetch_prices()` → recent prices
- `fetch_positions()` → `{"positions": [...], "avg_heat_index": float}`
- `fetch_system()` → `{"last_update_times": ..., "death_log": [...], "system_alerts": [...]}`
- Positions queries automatically apply the `heat_control` strategy if no
  strategy is provided, injecting heat thresholds and instructions into the
  context. This strategy relies on the `avg_heat_index` metric returned with
  the positions list.
