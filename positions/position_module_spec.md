# 💾 Position Module Specification

> Version: `v1.0`  
> Author: `CoreOps 🥷`  
> Scope: PositionCore + Enrichment + Sync + Hedge + Store  
> System: Cyclone Console + Engine + DL Layer

---

## 📂 Module Structure

```txt
positions/
├── position_core.py             # 🧠 Core orchestrator
├── position_store.py            # 💾 DB wrapper
├── position_enrichment_service.py # 🧬 Computes risk, value, travel, heat
├── position_sync_service.py     # 🔁 Jupiter sync (API ingestion)
├── hedge_manager.py             # 🔗 Groups hedges by size/collateral
🧠 PositionCore
Purpose
Central orchestrator for ingesting, enriching, syncing, snapshotting, and hedging position data.

Constructor
python
Copy
Edit
PositionCore(data_locker)
Accepts full DL for internal access to pricing, portfolio, system, positions, etc.

Methods
get_all_positions() → List[dict]
Loads all from store
Returns raw position dictionaries

get_active_positions() → List[dict]
Returns only records with status "ACTIVE"

create_position(pos_dict) → bool
Enriches position

Inserts into store

Logs success/failure via ConsoleLogger

delete_position(pos_id: str)
Passes through to store

Logs outcome

clear_all_positions()
Passes to store or DL

Used in reset/test cycles

record_snapshot()
Calls CalcServices.calculate_totals(...)

Delegates to DLPortfolioManager.record_snapshot(...)

Logs total size/value/collateral, averages, heat

update_positions_from_jupiter(source="console")
Wrapper to PositionSyncService.run_full_jupiter_sync()

Used in console and engine as backward-compatible API

link_hedges() → List[dict]
Uses HedgeManager.get_hedges() internally

Returns hedge objects

Logs count, groups, and validation tags

enrich_positions() → List[dict]
Similar to get_all_positions(), but logs per enrichment

Used as standalone operation in console engine cycle

🔁 PositionSyncService
Purpose
Ingests live positions from Jupiter wallets and stores them locally

Constructor
python
Copy
Edit
PositionSyncService(data_locker)
Main Method
run_full_jupiter_sync(source="console") → dict
Deletes all current positions

Calls update_jupiter_positions()

Enriches new ones

Rebuilds hedges

Records a snapshot

Updates system_vars with last sync timestamps

Logs every step

Internal Method
update_jupiter_positions() → dict
Loops through wallets

Hits Jupiter API: `${JUPITER_API_BASE}/v1/positions`

Maps and inserts valid positions

Skips failed or empty responses

Logs imported count and skips

🧬 PositionEnrichmentService
Purpose
Enriches a position with:

Leverage

Travel percent

Liquidation distance

Heat index (risk)

Constructor
python
Copy
Edit
PositionEnrichmentService(data_locker)
Method
enrich(pos_dict: dict) → dict
Uses CalcServices:

calculate_value()

calculate_leverage()

calculate_travel_percent()

calculate_liquid_distance()

calculate_composite_risk_index()

Injects market price via dl.prices.get_last_price_for(asset_type)

Logs results inline

🔗 HedgeManager
Purpose
Detects and groups hedge pairs from active positions.

Constructor
python
Copy
Edit
HedgeManager(positions: List[dict])
Methods
get_hedges() → List[dict]
Compares long/short matches across same asset

Looks at leverage, collateral size, wallet

Builds hedge candidates

Adds hedge_ratio, delta, imbalance

Logs hedge_count

clear_hedge_data()
Clears existing hedge state from file or memory

Rarely used — mostly for dev tools or CLI

💾 PositionStore
Purpose
Interacts directly with the positions table

Constructor
python
Copy
Edit
PositionStore(data_locker)
Methods
get_all() → List[dict]
Loads all positions from DB

Used by core + hedge + enrichment

get_by_id(pos_id: str) → dict
Single position lookup

insert(position: dict) → bool
Inserts fully-formed record

Expects enriched data

Injects default timestamps, logs failure reason

delete(pos_id: str)
Deletes by ID

delete_all()
Wipes table

Logs count if needed

⚙️ CalcServices (Used by Enrichment)
Method	Purpose
calculate_value()       collateral + P&L
calculate_leverage()	value ÷ collateral
calculate_travel_percent()	price deviation vs liquidation
calculate_liquid_distance()	dollar or % distance
calculate_composite_risk_index()	aggregation of leverage + travel + heat

🔐 SystemVars Touchpoints
last_update_time_positions

last_update_time_jupiter

last_update_positions_source

Set via dl.system.set_last_update_times({...}) during sync

🧠 Position Flow
Jupiter Sync
→ Fetch → parse → insert → enrich → snapshot → timestamp

Manual Create
→ Enrich → insert → log

Evaluate / Score
→ Enrich → snapshot → alertable

Hedge
→ Group positions → tag as hedge pair

View / Report
→ Enriched summary returned via get_all_positions()

🧩 Console/Engine Integration
Step	Uses
Update Positions	update_positions_from_jupiter()
Enrich Positions	enrich_positions()
Link Hedges	link_hedges()
Record Snapshot	record_snapshot()

✅ Design Philosophy
Core controls flow — no logic in UI/route

Services are single-purpose, composable

DB ops are isolated to PositionStore

ConsoleLogger used consistently for transparency

All enrichment & sync is testable end-to-end

