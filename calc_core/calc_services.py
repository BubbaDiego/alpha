import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Optional, List
from core.logging import log
from datetime import datetime
import sqlite3


class CalcServices:
    def __init__(self):
        self.color_ranges = {
            "travel_percent": [(0, 25, "green"), (25, 50, "yellow"), (50, 75, "orange"), (75, 100, "red")],
            "heat_index": [(0, 20, "blue"), (20, 40, "green"), (40, 60, "yellow"), (60, 80, "orange"), (80, 100, "red")],
            "collateral": [(0, 500, "lightgreen"), (500, 1000, "yellow"), (1000, 2000, "orange"), (2000, 10000, "red")]
        }
        self.weights = {
            "distanceWeight": 0.6,
            "leverageWeight": 0.3,
            "collateralWeight": 0.1
        }

    def calculate_composite_risk_index(self, position: dict) -> Optional[float]:
        try:
            entry_price = float(position.get("entry_price", 0.0))
            current_price = float(position.get("current_price", 0.0))
            liquidation_price = float(position.get("liquidation_price", 0.0))
            collateral = float(position.get("collateral", 0.0))
            size = float(position.get("size", 0.0))
            leverage = float(position.get("leverage", 0.0))
            position_type = (position.get("position_type") or "LONG").upper()

            if entry_price <= 0 or liquidation_price <= 0 or collateral <= 0 or size <= 0:
                return None
            if abs(entry_price - liquidation_price) < 1e-6:
                return None

            if position_type == "LONG":
                ndl = (current_price - liquidation_price) / (entry_price - liquidation_price)
            else:
                ndl = (liquidation_price - current_price) / (liquidation_price - entry_price)
            ndl = max(0.0, min(ndl, 1.0))

            distance_factor = 1.0 - ndl
            normalized_leverage = leverage / 100.0
            collateral_ratio = min(collateral / size, 1.0)
            risk_collateral_factor = 1.0 - collateral_ratio

            w = self.weights
            risk_index = (
                (distance_factor ** w["distanceWeight"]) *
                (normalized_leverage ** w["leverageWeight"]) *
                (risk_collateral_factor ** w["collateralWeight"]) * 100.0
            )

            risk_index = self.apply_minimum_risk_floor(risk_index, 5.0)
            risk_index = min(risk_index, 75.0)  # Cap to desired upper limit

            log.debug("Calculated composite risk index", "calculate_composite_risk_index", {
                "position_id": position.get("id"),
                "risk_index": risk_index,
                "weights": self.weights
            })

            return round(risk_index, 2)
        except Exception as e:
            log.error(f"Risk index calculation failed: {e}", "calculate_composite_risk_index", position)
            return None

    def calculate_value(self, position: dict) -> float:
        """Return the current value of a position.

        The value is defined as ``collateral + PnL`` where PnL is computed
        from the entry price, current price and position direction.
        """
        try:
            entry = float(position.get("entry_price") or 0.0)
            current = float(position.get("current_price") or 0.0)
            collateral = float(position.get("collateral") or 0.0)
            size = float(position.get("size") or 0.0)
            ptype = (position.get("position_type") or "LONG").upper()

            tokens = size / entry if entry else 0.0
            if ptype == "LONG":
                pnl = (current - entry) * tokens
            else:
                pnl = (entry - current) * tokens

            value = collateral + pnl
            value = round(value, 2)
            log.debug("Calculated value", "calculate_value", {"value": value})
            return value
        except Exception as e:
            log.error(f"Failed to calculate value: {e}", "calculate_value")
            return 0.0

    def calculate_leverage(self, size: float, collateral: float) -> float:
        leverage = round(size / collateral, 2) if size > 0 and collateral > 0 else 0.0
        log.debug("Calculated leverage", "calculate_leverage", {"leverage": leverage})
        return leverage

    def calculate_travel_percent(self, position_type: str, entry_price: float, current_price: float, liquidation_price: float) -> float:
        if entry_price <= 0 or liquidation_price <= 0:
            log.warning("Invalid price parameters in travel percent", "calculate_travel_percent")
            return 0.0

        ptype = position_type.strip().upper()
        result = 0.0

        try:
            if ptype == "LONG":
                if current_price <= entry_price:
                    denom = entry_price - liquidation_price
                    numer = current_price - entry_price
                    result = (numer / denom) * 100
                else:
                    profit_target = entry_price + (entry_price - liquidation_price)
                    result = ((current_price - entry_price) / (profit_target - entry_price)) * 100
            elif ptype == "SHORT":
                if current_price >= entry_price:
                    result = -((current_price - entry_price) / (liquidation_price - entry_price)) * 100
                else:
                    profit_target = entry_price - (liquidation_price - entry_price)
                    result = ((entry_price - current_price) / (entry_price - profit_target)) * 100
            else:
                log.warning(f"Unknown position type {position_type}", "calculate_travel_percent")
        except Exception as e:
            log.error(f"Failed to calculate travel percent: {e}", "calculate_travel_percent")

        log.debug("Travel percent calculated", "calculate_travel_percent", {"result": result})
        return result

    def calculate_liquid_distance(self, current_price: float, liquidation_price: float) -> float:
        distance = round(abs(liquidation_price - current_price), 2)
        log.debug("Calculated liquidation distance", "calculate_liquid_distance", {"distance": distance})
        return distance

    def calculate_heat_index(self, position: dict) -> Optional[float]:
        try:
            size = float(position.get("size", 0.0))
            leverage = float(position.get("leverage", 0.0))
            collateral = float(position.get("collateral", 0.0))
            if collateral <= 0:
                return None
            hi = (size * leverage) / collateral
            log.debug("Heat index calculated", "calculate_heat_index", {"heat_index": hi})
            return round(hi, 2)
        except Exception as e:
            log.error(f"Failed to calculate heat index: {e}", "calculate_heat_index", position)
            return None

    def calculate_weighted_heat_index(self, positions: List[dict]) -> float:
        """Return size-weighted average heat index for ``positions``."""
        total_weighted = 0.0
        total_size = 0.0
        for pos in positions:
            hi = float(pos.get("heat_index") or 0.0)
            size = float(pos.get("size") or 1.0)
            if size == 0:
                size = 1.0
            total_weighted += hi * size
            total_size += size
        return total_weighted / total_size if total_size > 0 else 0.0

    def calculate_totals(self, positions: List[dict]) -> dict:
        log.info("Calculating totals from positions", "calculate_totals")
        total_size = total_value = total_collateral = 0.0
        weighted_leverage_sum = weighted_travel_percent_sum = 0.0

        for pos in positions:
            size = float(pos.get("size") or 0.0)
            value = float(pos.get("value") or 0.0)
            collateral = float(pos.get("collateral") or 0.0)
            leverage = float(pos.get("leverage") or 0.0)
            travel_percent = float(pos.get("travel_percent") or 0.0)

            total_size += size
            total_value += value
            total_collateral += collateral
            weighted_leverage_sum += leverage * size
            weighted_travel_percent_sum += travel_percent * size

        avg_leverage = weighted_leverage_sum / total_size if total_size > 0 else 0.0
        avg_travel_percent = weighted_travel_percent_sum / total_size if total_size > 0 else 0.0
        avg_heat_index = self.calculate_weighted_heat_index(positions)

        totals = {
            "total_size": total_size,
            "total_value": total_value,
            "total_collateral": total_collateral,
            "avg_leverage": avg_leverage,
            "avg_travel_percent": avg_travel_percent,
            "avg_heat_index": avg_heat_index
        }

        log.success("Totals calculated", "calculate_totals", totals)
        return totals

    def apply_minimum_risk_floor(self, risk_index: float, floor: float = 5.0) -> float:
        return max(risk_index, floor)

    def get_color(self, value: float, metric: str) -> str:
        if metric not in self.color_ranges:
            return "white"
        for (lower, upper, color) in self.color_ranges[metric]:
            if lower <= value < upper:
                return color
        return "red"

    # ------------------------------------------------------------------
    # Price evaluation helpers
    # ------------------------------------------------------------------
    def value_at_price(self, position: dict, price: float) -> float:
        """Return the position value using ``price`` as the current price."""
        entry = float(position.get("entry_price", 0.0))
        collateral = float(position.get("collateral", 0.0))
        size = float(position.get("size", 0.0))
        ptype = (position.get("position_type") or "LONG").upper()

        tokens = size / entry if entry else 0.0
        if ptype == "LONG":
            pnl = (price - entry) * tokens
        else:
            pnl = (entry - price) * tokens

        return round(collateral + pnl, 2)

    def travel_percent_at_price(self, position: dict, price: float) -> float:
        """Calculate travel percent at a given ``price``."""
        return self.calculate_travel_percent(
            position.get("position_type", "LONG"),
            float(position.get("entry_price", 0.0)),
            price,
            float(position.get("liquidation_price", 0.0)),
        )

    def liquid_distance_at_price(self, position: dict, price: float) -> float:
        """Liquidation distance using ``price`` as the current price."""
        return self.calculate_liquid_distance(
            price, float(position.get("liquidation_price", 0.0))
        )

    def heat_index_at_price(self, position: dict, price: float) -> Optional[float]:
        """Composite heat index if the position were at ``price``."""
        pos_copy = dict(position)
        pos_copy["current_price"] = price
        pos_copy.setdefault(
            "leverage",
            self.calculate_leverage(
                float(position.get("size", 0.0)),
                float(position.get("collateral", 0.0)),
            ),
        )
        return self.calculate_composite_risk_index(pos_copy) or 0.0

    def evaluate_at_price(self, position: dict, price: float) -> dict:
        """Return multiple metrics for ``position`` evaluated at ``price``."""
        return {
            "value": self.value_at_price(position, price),
            "travel_percent": self.travel_percent_at_price(position, price),
            "liquidation_distance": self.liquid_distance_at_price(position, price),
            "heat_index": self.heat_index_at_price(position, price),
        }

