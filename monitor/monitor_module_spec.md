# 🛰️ Monitor Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Monitor orchestrator and supporting monitors.

---

## 📂 Module Structure

```txt
monitor/
├── monitor_core.py         # 🚦 Registers and runs monitors
├── base_monitor.py         # 🔧 Shared run_cycle/ledger wrapper
├── monitor_registry.py     # 📇 Holds monitor instances
├── price_monitor.py        # 💰 Fetches prices from APIs
├── position_monitor.py     # 📈 Syncs and enriches positions
├── operations_monitor.py   # 🧪 Startup POST tests and health checks
├── latency_monitor.py      # ⏱️ External API latency checker
├── ledger_service.py       # 🧾 JSON ledger utilities
├── monitor_api.py          # 🌐 Flask API endpoints
└── sonic_monitor.py        # ❤️ Background cycle runner
```

### 🚦 MonitorCore
Central controller for executing registered monitors.

```python
MonitorCore(registry: MonitorRegistry | None = None)
```
- If `registry` is not provided, a new one is created and default monitors are registered (`PriceMonitor`, `PositionMonitor`, `OperationsMonitor`).

**Methods**
- `run_all()` – iterate and run every monitor in the registry, logging success or failure.
- `run_by_name(name)` – run a single monitor by its key if present.

### 🧩 Monitor Implementations
- **BaseMonitor** – provides `run_cycle()` wrapper that records results in the database ledger.
- **PriceMonitor** – fetches BTC/ETH/SOL prices via `MonitorService`.
- **PositionMonitor** – syncs positions from Jupiter and logs summary metrics.
- **OperationsMonitor** – runs POST tests on startup and stores results.
- **LatencyMonitor** – optional HTTP latency checker for third-party services.

### 🌐 API & Background Runner
- `monitor_api.py` exposes REST endpoints to trigger monitors individually or all at once.
- `sonic_monitor.py` runs periodic cycles using `Cyclone` and records a heartbeat in the database.

### ✅ Design Notes
- Monitors write a summary entry to the ledger table via `DataLocker.ledger`.
- Registration through `MonitorRegistry` keeps monitor setup centralized.
- Execution paths include CLI scripts, Flask API, and long‑running background loops.
