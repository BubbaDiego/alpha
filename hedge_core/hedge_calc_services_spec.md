# 📐 HedgeCalcServices Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Delta and gamma hedging calculations for opposing positions.

`HedgeCalcServices` is a calculation utility supporting delta and gamma hedging workflows. It evaluates paired long and short positions, measures imbalance, and suggests rebalancing actions.

---

## 🎯 Goals
- Simulate value, PnL, and imbalance at any price.
- Suggest rebalances by adjusting `size`, `collateral`, or `leverage`.
- Enable delta/gamma hedging via exposure modeling.
- Allow user configurable strategies and constraints.

## 📦 Inputs

### Position Object
```json
{
  "id": "uuid",
  "position_type": "LONG" | "SHORT",
  "entry_price": float,
  "size": float,
  "collateral": float,
  "leverage": float,
  "liquidation_price": float
}
```

### Hedge Pair Input
```python
(long_position: dict, short_position: dict, price: float, config: dict)
```

### Config Example
```json
{
  "adjustment_target": "equal_value",
  "adjustable_side": "long",
  "adjust_fields": ["size", "collateral"]
}
```

## 🛠️ Core Methods

### 1. `evaluate_at_price(long_pos, short_pos, price) -> dict`
Returns evaluation details for both positions at the supplied price.

### 2. `suggest_rebalance(long_pos, short_pos, price, config) -> dict`
Proposes how to rebalance the selected side to meet a target strategy.
Supported targets:
- `equal_value` – equalize the value at the current price.
- `delta_neutral` – adjust to make combined delta ~0.
- `gamma_flat` – match gamma exposures (optional).

### 3. `simulate_range(long_pos, short_pos, price_range) -> list[dict]`
Evaluates the pair across a set of prices for graphing and UI sliders.

## 🧪 Testing Strategy
- Unit tests for known PnL and value outputs.
- Rebalance suggestions where the imbalance is clear.

## 🧠 Future Expansion
- Support multiple position groups.
- Historical backtesting of strategies.
- Deeper derivative modeling for delta/gamma calculations.

## 📎 Notes
- This service is purely mathematical—no DB operations.
- All values are floats rounded to 6 decimals unless configured.
