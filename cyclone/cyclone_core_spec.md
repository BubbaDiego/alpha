# 🌪️ Cyclone Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Orchestration engine for market updates, position enrichment, alert creation, hedge linkage, and reporting.

---

## 📂 Module Structure
```txt
cyclone/
├── cyclone_engine.py          # 🌪️ Cyclone class and run_cycle entry point
├── cyclone_alert_service.py   # 🚨 Generates and evaluates alerts
├── cyclone_position_service.py# 📊 Position operations and enrichment
├── cyclone_portfolio_service.py # 📈 Portfolio alert helpers
├── cyclone_hedge_service.py   # 🔗 Hedge detection wrapper
├── cyclone_wallet_service.py  # 👛 Wallet management utilities
├── cyclone_report_generator.py# 📝 HTML report builder
├── cyclone_console/           # 🎛️ Rich CLI interface
├── cyclone_bp.py              # 🌐 Flask Blueprint endpoints
```

## 🌪️ `Cyclone` Class
Central orchestrator defined in `cyclone_engine.py`.

### Constructor
```python
Cyclone(monitor_core, poll_interval=60)
```
- Initializes a shared `DataLocker` instance.
- Creates `PositionCore`, `AlertCore`, `PriceSyncService`, and helper services.
- Configures the central logger via `configure_cyclone_console_log()`.

### Key Methods
- `async run_cycle(steps=None)` – runs a sequence of operations such as price updates, position enrichment, hedge linking, and alert evaluation.
- `async run_market_updates()` – fetches latest prices using `PriceSyncService`.
- `async run_enrich_positions()` – enriches all positions via `PositionCore`.
- `async run_create_position_alerts()` – generates position level alerts.
- `async run_create_portfolio_alerts()` – generates portfolio level alerts.
- `async run_alert_evaluation()` – evaluates alert levels after enrichment.
- `async run_link_hedges()` – detects hedge pairs using `CycloneHedgeService`.
- `async run_cleanse_ids()` – clears stale alerts from the datastore.
- `async run_update_hedges()` – refreshes hedge groups after linking.

The default cycle executes steps in order:
`update_operations`, `market_updates`, `check_jupiter_for_updates`,
`enrich_positions`, `enrich_alerts`, `update_evaluated_value`,
`create_market_alerts`, `create_portfolio_alerts`, `create_position_alerts`,
`create_global_alerts`, `evaluate_alerts`, `cleanse_ids`, `link_hedges`,
`update_hedges`.

Each method logs progress with emojis and delegates to the appropriate service or core module.

## 🧩 Integrations
- **DataLocker** – provides persistence for alerts, prices, positions, and system variables.
- **AlertCore** – all alert creation and evaluation flows.
- **PositionCore** – position synchronization and enrichment.
- **MonitorCore** – optional monitoring callbacks during `run_cycle`.
- **Flask API** – `cyclone_bp.py` exposes HTTP endpoints that call into the same run methods.
- **Console** – `cyclone_console` offers an interactive menu using the `rich` library.

## ✅ Design Notes
- Steps are asynchronous and can be executed individually or as a full cycle.
- Centralized logging tags each message with the Cyclone source for clarity.
- Error handling in `run_cycle` emits "death" events through `SystemCore` when a step fails fatally.
- The architecture keeps services thin so logic is reusable in both CLI and API contexts.

