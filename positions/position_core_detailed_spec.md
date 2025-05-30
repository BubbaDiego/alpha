# Position Core Detailed Specification

## Overview

The `PositionCore` module orchestrates position management, enrichment, synchronization, and snapshotting. It relies on the `DataLocker` data layer for persistent storage and shared services.  This specification documents the behavior of `PositionCore`, its interaction with subordinate services (`PositionStore`, `PositionEnrichmentService`, `PositionSyncService`, and `HedgeManager`), and the responsibilities of the data layer components it uses.

## Module Relationships

```
PositionCore
 ├─ PositionStore             → wrappers around DataLocker.positions
 ├─ PositionEnrichmentService → uses CalculationCore and DataLocker.prices
 ├─ PositionSyncService       → fetches from Jupiter API, inserts via DataLocker
 └─ HedgeManager              → pure in‑memory hedge detection
DataLocker
 ├─ DatabaseManager           → SQLite wrapper
 ├─ DLPositionManager         → CRUD for `positions` table
 ├─ DLPortfolioManager        → records portfolio snapshots
 ├─ DLSystemDataManager       → stores system vars (update times, theme, etc.)
 └─ other managers (alerts, prices, wallets, …)
```

`PositionCore` receives a `DataLocker` instance at construction and passes it to all sub‑components. Because `DataLocker` holds an open connection to the SQLite database, all position operations ultimately go through `DLPositionManager`.

## DataLocker Schema

The relevant schema for positions is created in `DataLocker.initialize_database()`:

```python
# data/data_locker.py
130  "positions": """
131      CREATE TABLE IF NOT EXISTS positions (
132          id TEXT PRIMARY KEY,
133          asset_type TEXT,
134          position_type TEXT,
135          entry_price REAL,
136          liquidation_price REAL,
137          travel_percent REAL,
138          value REAL,
139          collateral REAL,
140          size REAL,
141          leverage REAL,
142          wallet_name TEXT,
143          last_updated TEXT,
144          alert_reference_id TEXT,
145          hedge_buddy_id TEXT,
146          current_price REAL,
147          liquidation_distance REAL,
148          heat_index REAL,
149          current_heat_index REAL,
150          pnl_after_fees_usd REAL
151      )
"""
```

This table stores every imported or manually created position. `DLPositionManager` operates on this table.

Additional tables used by `PositionCore` workflows:

- `positions_totals_history` for snapshots (`DLPortfolioManager.record_snapshot`).
- `system_vars` where last update timestamps are kept (`DLSystemDataManager`).

## `PositionCore` Class

### Construction

```python
# positions/position_core.py
13 class PositionCore:
14     def __init__(self, data_locker):
15         self.dl = data_locker
16         self.store = PositionStore(data_locker)
17         self.enricher = PositionEnrichmentService(data_locker)
```

Upon instantiation, `PositionCore` keeps a reference to the provided `DataLocker` and initializes two helpers:

- `PositionStore` – thin wrapper over `DLPositionManager` for CRUD operations.
- `PositionEnrichmentService` – calculates leverage, travel percent, heat index, and injects live prices.

### Basic CRUD

```python
19 def get_all_positions(self):
20     return self.store.get_all_positions()

22 def get_active_positions(self):
23     return self.store.get_active_positions()

25 def create_position(self, pos: dict):
26     enriched = self.enricher.enrich(pos)
27     return self.store.insert(enriched)

29 def delete_position(self, pos_id: str):
30     return self.store.delete(pos_id)

32 def clear_all_positions(self):
33     self.store.delete_all()
```

- `get_all_positions()` fetches all rows via `PositionStore.get_all()`, which calls `DataLocker.positions.get_all_positions()`.
- `create_position()` enriches the provided dictionary then inserts it via `DLPositionManager.create_position()`.
- `delete_position()` and `clear_all_positions()` map to `DLPositionManager.delete_position` and `DLPositionManager.delete_all_positions` respectively.

### Snapshot Recording

```python
35 def record_snapshot(self):
36     try:
37         raw = self.store.get_all()
38         totals = CalcServices().calculate_totals(raw)
39         self.dl.portfolio.record_snapshot(totals)
40         log.success("📸 Position snapshot recorded", source="PositionCore")
41     except Exception as e:
42         log.error(f"❌ Snapshot recording failed: {e}", source="PositionCore")
```

Snapshots summarize all positions into aggregate metrics and store them using `DLPortfolioManager.record_snapshot`. The `CalcServices.calculate_totals()` utility computes totals (size, value, collateral) plus averages such as leverage and heat index. The resulting data is persisted in `positions_totals_history`.

### Jupiter Synchronization

```python
44 def update_positions_from_jupiter(self, source="console"):
49     from positions.position_sync_service import PositionSyncService
50     sync_service = PositionSyncService(self.dl)
51     return sync_service.run_full_jupiter_sync(source=source)
```

This delegates to `PositionSyncService`. During a full sync the service:
1. Calls `update_jupiter_positions()` to fetch wallet positions from the Jupiter API and insert them into the database via `DLPositionManager.create_position`.
2. Generates hedges with `HedgeManager`.
3. Updates timestamps in `system_vars` with `DLSystemDataManager.set_last_update_times`.
4. Records a portfolio snapshot using `DLPortfolioManager`.

### Hedge Linking

```python
53 def link_hedges(self):
57     log.banner("🔗 Generating Hedges via PositionCore")
60     positions = self.store.get_all()
63     hedge_manager = HedgeManager(positions)
64     hedges = hedge_manager.get_hedges()
66     log.success("✅ Hedge generation complete", source="PositionCore", payload={"hedge_count": len(hedges)})
67     return hedges
```

`HedgeManager` analyzes in‑memory positions to pair long and short exposures. The resulting hedge records are not persisted by `PositionCore` directly but may be inserted via other DataLocker utilities if required.

### Enrichment of Existing Positions

```python
73 async def enrich_positions(self):
78     log.banner("🧠 Enriching All Positions via PositionCore")
81     raw = self.store.get_all()
82     enriched = []
83     failed = []
85     for pos in raw:
87         enriched_pos = self.enricher.enrich(pos)
89         if validate_enriched_position(enriched_pos, source="EnrichmentValidator"):
90             enriched.append(enriched_pos)
91         else:
92             failed.append(enriched_pos.get("id"))
97     log.success("✅ Position enrichment complete", source="PositionCore", payload={"enriched": len(enriched), "failed": len(failed)})
102     if failed:
103         log.warning("⚠️ Some positions failed enrichment validation", source="PositionCore", payload={"invalid_ids": failed})
107     return enriched
```

This method reloads all positions, enriches each using `PositionEnrichmentService`, validates them, and returns the enriched list (without writing back to the database). Failures are logged for review.

## `PositionStore`

`PositionStore` is a very small wrapper around `DLPositionManager`. Key methods:

```python
11 class PositionStore:
15     def get_all(self) -> list:
17         rows = self.dl.positions.get_all_positions()

27 def get_active_positions(self) -> list:
29     cursor = self.dl.db.get_cursor()
30     cursor.execute("SELECT * FROM positions WHERE status = 'ACTIVE'")
31     rows = cursor.fetchall()

41 def insert(self, position: dict) -> bool:
45     self.dl.positions.create_position(position)

52 def delete(self, pos_id: str) -> bool:
54     self.dl.positions.delete_position(pos_id)

61 def delete_all(self):
63     self.dl.positions.delete_all_positions()
```

Because `DataLocker` already exposes `DLPositionManager`, `PositionStore` mainly adds logging and default fields.

## `DLPositionManager`

The data layer implementation for positions resides here. Highlights:

- **Defaults & Sanitization** – `create_position()` inserts defaults for all missing fields before writing to the database and strips any keys not present in the schema. [`data/dl_positions.py` lines 33‑71]【F:data/dl_positions.py†L33-L71】
- **Retrieval** – `get_all_positions()` returns a list of dictionaries for all rows. [`data/dl_positions.py` lines 109‑118]【F:data/dl_positions.py†L109-L118】
- **Deletion** – `delete_position()` and `delete_all_positions()` remove rows from the table. [`data/dl_positions.py` lines 124‑142]【F:data/dl_positions.py†L124-L142】
- **Snapshots** – `record_positions_totals_snapshot()` persists aggregate metrics to `positions_totals_history`. [`data/dl_positions.py` lines 152‑176】

## Data Flow Example

Creating a position via `PositionCore.create_position()` proceeds as follows:

1. Caller supplies a basic position dictionary.
2. `PositionEnrichmentService.enrich()` computes derived fields such as leverage, heat index, and injects current market price via `DataLocker.prices.get_latest_price`.
3. The enriched dictionary is passed to `PositionStore.insert()`.
4. `PositionStore` calls `DLPositionManager.create_position()` which ensures defaults, sanitizes fields against the schema, constructs the SQL insert, and commits to SQLite.
5. Success is logged at each stage via the centralized logger.

## Snapshot Lifecycle

When `record_snapshot()` is invoked:

1. All positions are loaded from the database.
2. `CalcServices.calculate_totals()` computes totals and averages.
3. `DLPortfolioManager.record_snapshot()` writes these aggregates to `positions_totals_history` with a timestamp.
4. The operation is logged as a success or failure.

## Timestamp Management

`PositionSyncService` and other callers use `DataLocker.system.set_last_update_times()` to record when data was last refreshed. The `system_vars` table holds fields such as `last_update_time_positions`, `last_update_time_jupiter`, and their corresponding source labels. This ensures UI components can display the freshness of data.

## Error Handling & Logging

Throughout the module stack, errors are caught and logged with the same console logger (`core.logging`). Failures to write to the database are logged both to the console and, in the case of `DLPositionManager.create_position`, to a persistent log file (`logs/dl_failed_inserts.log`) so that problematic payloads can be inspected later.

## Summary

`PositionCore` is the high‑level API for anything related to trading positions. It delegates storage to `DataLocker`’s managers and uses enrichment logic to ensure positions carry calculated metrics. By combining synchronization, enrichment, hedge detection, and snapshotting, it provides a single entry point for the rest of the application (Flask routes, console tools, and monitoring engine) to manage position data in a consistent manner.
