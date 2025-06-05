import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from datetime import datetime
from core.logging import log
from calc_core.calc_services import CalcServices
import sqlite3


class CalculationCore:
    def __init__(self, data_locker):
        self.data_locker = data_locker
        self.calc_services = CalcServices()
        self.modifiers = self._load_modifiers()

    def _load_modifiers(self):
        cursor = self.data_locker.db.get_cursor()
        if not cursor:
            log.error("❌ DB unavailable, using default modifiers", source="CalculationCore")
            weights = self.calc_services.weights
            return weights

        try:
            rows = cursor.execute(
                "SELECT key, value FROM modifiers WHERE group_name = 'heat_modifiers'"
            ).fetchall()
            weights = {row['key']: float(row['value']) for row in rows}
        except Exception as e:
            log.error(f"❌ Failed loading modifiers: {e}", source="CalculationCore")
            weights = {}

        if not weights:
            log.warning("⚠️ No modifiers found in DB; falling back to default", source="CalculationCore")
            weights = {
                "distanceWeight": 0.6,
                "leverageWeight": 0.3,
                "collateralWeight": 0.1
            }

        self.calc_services.weights = weights  # inject into CalcServices
        log.success("✅ Modifiers loaded into CalcServices", source="CalculationCore", payload=weights)
        return weights

    def get_heat_index(self, position: dict) -> float:
        return self.calc_services.calculate_composite_risk_index(position)

    def get_travel_percent(self, position_type, entry_price, current_price, liquidation_price):
        return self.calc_services.calculate_travel_percent(
            position_type, entry_price, current_price, liquidation_price
        )

    def aggregate_positions_and_update(self, positions: list, db_path: str) -> list:
        log.start_timer("aggregate_positions_and_update")
        log.info("Starting aggregation on positions", "aggregate_positions_and_update", {"count": len(positions)})

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for pos in positions:
            pos_id = pos.get("id", "UNKNOWN")
            try:
                log.debug(f"Aggregating position {pos_id}", "aggregate_positions_and_update", pos)

                position_type = (pos.get("position_type") or "LONG").upper()
                entry_price = float(pos.get("entry_price", 0.0))
                current_price = float(pos.get("current_price", 0.0))
                liquidation_price = float(pos.get("liquidation_price", 0.0))
                collateral = float(pos.get("collateral", 0.0))
                size = float(pos.get("size", 0.0))

                pos["travel_percent"] = self.calc_services.calculate_travel_percent(
                    position_type, entry_price, current_price, liquidation_price
                )
                pos["liquidation_distance"] = self.calc_services.calculate_liquid_distance(current_price, liquidation_price)

                for field, val in [
                    ("travel_percent", pos["travel_percent"]),
                    ("liquidation_distance", pos["liquidation_distance"]),
                    ("current_price", current_price)
                ]:
                    cursor.execute(f"UPDATE positions SET {field} = ? WHERE id = ?", (val, pos_id))

                pos["value"] = self.calc_services.calculate_value(pos)
                pos["pnl_after_fees_usd"] = self.calc_services.calculate_profit(pos)
                pos["leverage"] = round(size / collateral, 2) if collateral > 0 else 0.0
                heat_index = self.calc_services.calculate_composite_risk_index(pos) or 0.0
                pos["heat_index"] = pos["current_heat_index"] = heat_index

                cursor.execute(
                    "UPDATE positions SET value = ?, pnl_after_fees_usd = ?, heat_index = ?, current_heat_index = ? WHERE id = ?",
                    (pos["value"], pos["pnl_after_fees_usd"], heat_index, heat_index, pos_id),
                )
                log.success("Updated DB for position", "aggregate_positions_and_update", {"id": pos_id, "heat_index": heat_index})

            except Exception as e:
                log.error(f"Error processing position {pos_id}: {e}", "aggregate_positions_and_update")

        conn.commit()
        conn.close()
        log.end_timer("aggregate_positions_and_update", "aggregate_positions_and_update")
        return positions

    def set_modifier(self, key: str, value: float):
        cursor = self.data_locker.db.get_cursor()
        cursor.execute("""
            INSERT INTO modifiers (key, group_name, value, last_modified)
            VALUES (?, 'heat_modifiers', ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, last_modified = excluded.last_modified
        """, (key, value, datetime.now().isoformat()))
        self.data_locker.db.commit()
        self.modifiers[key] = value
        self.calc_services.weights[key] = value
        log.success(f"✅ Modifier updated: {key} = {value}", source="CalculationCore")

    def export_modifiers(self) -> str:
        return json.dumps({"heat_modifiers": self.modifiers}, indent=2)

    def import_modifiers(self, json_data: str):
        data = json.loads(json_data)
        heat_mods = data.get("heat_modifiers", {})
        for key, value in heat_mods.items():
            self.set_modifier(key, float(value))
        log.success("📦 Modifiers imported from JSON", source="CalculationCore")

    def calculate_totals(self, positions: list) -> dict:
        """Return aggregated totals for the provided positions."""
        return self.calc_services.calculate_totals(positions)
