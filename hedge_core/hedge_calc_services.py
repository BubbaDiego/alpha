from __future__ import annotations

from typing import List, Dict


class HedgeCalcServices:
    """Utility class for simple hedge evaluations and rebalancing suggestions."""

    @staticmethod
    def _eval_position(pos: dict, price: float) -> Dict[str, float]:
        entry = float(pos.get("entry_price", 0.0))
        size = float(pos.get("size", 0.0))
        collateral = float(pos.get("collateral", 0.0))
        ptype = (pos.get("position_type") or "LONG").upper()

        tokens = size / entry if entry else 0.0

        if ptype == "LONG":
            pnl = (price - entry) * tokens
            delta = tokens
        else:
            pnl = (entry - price) * tokens
            delta = -tokens

        value = collateral + pnl

        return {
            "value": round(value, 6),
            "pnl": round(pnl, 6),
            "delta": round(delta, 6),
            "gamma": 0.0,
            "collateral": collateral,
            "size": size,
        }

    def evaluate_at_price(self, long_pos: dict, short_pos: dict, price: float) -> Dict[str, Dict[str, float]]:
        """Return PnL and value metrics for both positions at a specific price."""
        long_eval = self._eval_position(long_pos, price)
        short_eval = self._eval_position(short_pos, price)

        net = {
            "value": round(long_eval["value"] + short_eval["value"], 6),
            "pnl": round(long_eval["pnl"] + short_eval["pnl"], 6),
            "delta": round(long_eval["delta"] + short_eval["delta"], 6),
            "gamma": round(long_eval["gamma"] + short_eval["gamma"], 6),
            "imbalance": round(long_eval["value"] - short_eval["value"], 6),
        }
        return {"long": long_eval, "short": short_eval, "net": net}

    def suggest_rebalance(self, long_pos: dict, short_pos: dict, price: float, config: dict) -> Dict[str, object]:
        """Suggest basic rebalance actions based on the provided strategy."""
        eval_data = self.evaluate_at_price(long_pos, short_pos, price)

        target = (config.get("adjustment_target") or "equal_value").lower()
        side = (config.get("adjustable_side") or "long").lower()
        fields: List[str] = config.get("adjust_fields", ["collateral"])

        suggestion = {"side": side, "updates": {}}

        if target == "equal_value":
            long_val = eval_data["long"]["value"]
            short_val = eval_data["short"]["value"]
            diff = short_val - long_val if side == "long" else long_val - short_val
            pos = long_pos if side == "long" else short_pos

            if "collateral" in fields:
                new_collateral = pos.get("collateral", 0.0) + diff
                suggestion["updates"]["collateral"] = round(new_collateral, 6)
                diff -= diff  # fully accounted for

            if "size" in fields and abs(diff) > 0.0:
                entry = float(pos.get("entry_price", 0.0))
                if entry > 0:
                    tokens = diff / price
                    new_size = pos.get("size", 0.0) + tokens * entry
                else:
                    new_size = pos.get("size", 0.0)
                suggestion["updates"]["size"] = round(new_size, 6)
        else:
            suggestion["note"] = "strategy not implemented"

        return suggestion

    def simulate_range(self, long_pos: dict, short_pos: dict, price_range: List[float]) -> List[Dict[str, Dict[str, float]]]:
        """Evaluate the hedge pair across multiple prices."""
        return [self.evaluate_at_price(long_pos, short_pos, p) for p in price_range]
