# 🧮 Calculation Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Risk metric calculations, aggregation utilities, and hedge grouping.

---

## 📂 Module Structure

```txt
calc_core/
├── calculation_core.py  # 🧮 Loads modifiers, updates DB fields, aggregates totals
├── calc_services.py     # ⚙️ Pure math utilities for leverage and risk metrics
├── hedge_manager.py     # 🌿 Groups positions into hedges
```

### 🧮 CalculationCore
Purpose
Central orchestrator for risk calculations and DB updates.

Constructor
```python
CalculationCore(data_locker)
```
`data_locker`: DataLocker instance for database access.

Methods
- `get_heat_index(position: dict) -> float` – composite risk index via CalcServices.
- `get_travel_percent(position_type, entry_price, current_price, liquidation_price)` – wrapper over CalcServices.
- `aggregate_positions_and_update(positions: list, db_path: str) -> list` – updates DB with travel %, liquidation distance, value, leverage, and heat index.
- `set_modifier(key: str, value: float)` – persist heat index weighting factors.
- `export_modifiers() -> str` – export modifiers as JSON.
- `import_modifiers(json_data: str)` – import and apply modifier values.
- `calculate_totals(positions: list) -> dict` – return aggregated totals via CalcServices.

### ⚙️ CalcServices
Purpose
Collection of pure functions for risk and position metrics.

Key Methods
- `calculate_composite_risk_index(position: dict) -> Optional[float>`
- `calculate_value(position) -> float`
- `calculate_leverage(size: float, collateral: float) -> float`
- `calculate_travel_percent(position_type, entry_price, current_price, liquidation_price) -> float`
- `calculate_liquid_distance(current_price, liquidation_price) -> float`
- `calculate_heat_index(position: dict) -> Optional[float>`
- `calculate_totals(positions: List[dict]) -> dict`
- `apply_minimum_risk_floor(risk_index, floor=5.0)`
- `get_color(value: float, metric: str) -> str`

### 🌿 HedgeManager
Purpose
Detects and groups hedges from position sets.

Highlights
- `build_hedges()` forms `Hedge` objects from positions sharing `hedge_buddy_id`.
- `find_hedges(db_path)` scans the database for long/short pairs and assigns hedge IDs.
- `clear_hedge_data(db_path)` removes hedge associations in bulk.
- `get_hedges()` returns the computed hedge list.

🧩 Integrations
- `PositionCore` uses `CalculationCore` for enrichment and portfolio snapshots.
- `Cyclone` engine can trigger `HedgeManager.find_hedges()` during risk evaluation cycles.

✅ Design Notes
- Calculations are logged via `ConsoleLogger` for transparency.
- Modifier weights allow runtime tuning of risk formulas without redeploying code.
- CalcServices is stateless and easily unit tested.
