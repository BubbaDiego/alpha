# 🌿 Hedge Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Grouping and managing hedges derived from position data.

---

## 📂 Module Structure

```txt
hedge_core/
├── hedge_core.py  # 🔗 Builds and links hedges
```

### 🔗 `HedgeCore`
Central orchestrator that creates, links, and fetches hedge objects.

```python
HedgeCore(data_locker)
```
- `data_locker`: instance of `DataLocker` providing DB access and helper managers.

**Key Methods**
- `update_hedges()` – orchestrates linking and building hedges from live positions.
- `build_hedges(positions=None) -> List[Hedge]` – converts position records into `Hedge` objects grouped by `hedge_buddy_id`.
- `link_hedges() -> List[list]` – scans current positions and assigns a shared UUID to long/short pairs.
- `unlink_hedges()` – clears all `hedge_buddy_id` values in the database.
- `get_modifiers(group=None) -> dict` – returns hedge/heat modifiers via `DLModifierManager`.
- `get_db_hedges() -> List[Hedge]` – retrieves persisted hedges using `DLHedgeManager`.

### 🗂️ Data Flow
1. `update_hedges()` logs the refresh, invokes `HedgeManager.find_hedges()` and builds results. 【F:hedge_core/hedge_core.py†L24-L41】
2. `build_hedges()` groups positions by `hedge_buddy_id`, aggregates sizes and heat indices, and returns a list of `Hedge` objects. 【F:hedge_core/hedge_core.py†L43-L89】
3. `link_hedges()` iterates positions grouped by `(wallet_name, asset_type)` and assigns a UUID when both long and short types are present. 【F:hedge_core/hedge_core.py†L91-L118】
4. `unlink_hedges()` performs a bulk SQL update to remove links. 【F:hedge_core/hedge_core.py†L121-L129】

### ✅ Design Notes
- All logging is handled through the shared logger injected via `core.core_imports`. 【F:hedge_core/hedge_core.py†L24-L129】
- Hedge detection relies solely on wallet/asset pairs and does not consider leverage or size weighting in this implementation.
- Hedge IDs are set to the `hedge_buddy_id` so they remain consistent between calls.
- `get_modifiers()` provides a simple pass-through to the data layer so external callers can inspect weighting factors.

