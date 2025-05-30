import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from positions.position_enrichment_service import PositionEnrichmentService, validate_enriched_position
from calc_core.calculation_core import CalculationCore
from core.logging import log

class PositionCoreService:
    def __init__(self, data_locker):
        self.dl = data_locker

    def fill_positions_with_latest_price(self, positions):
        for pos in positions:
            asset = pos.get('asset_type')
            if asset:
                latest = self.dl.get_latest_price(asset)
                if latest and 'current_price' in latest:
                    try:
                        pos['current_price'] = float(latest['current_price'])
                    except Exception as e:
                        log.warning(f"⚠️ Couldn't parse latest price for {asset}: {e}", source="PositionCoreService")
        return positions

    def update_position_and_alert(self, pos):
        try:
            self.dl.positions.create_position(pos)
            from alert_core.alert_evaluator import AlertEvaluator
            evaluator = AlertEvaluator({}, self.dl)
            evaluator.update_alert_for_position(pos)
            log.success(f"✅ Updated position & alert: {pos.get('id')}", source="PositionCoreService")
        except Exception as e:
            log.error(f"❌ update_position_and_alert failed: {e}", source="PositionCoreService")

    def delete_position_and_cleanup(self, position_id: str):
        try:
            from alert_core.alert_controller import AlertController
            alert_ctrl = AlertController()

            alerts = self.dl.get_alerts()
            alerts_deleted = 0
            for alert in alerts:
                if alert.get("position_reference_id") == position_id:
                    if alert_ctrl.delete_alert(alert["id"]):
                        alerts_deleted += 1
            log.success(f"🗑 Deleted {alerts_deleted} alerts for position {position_id}", source="PositionCoreService")

            cursor = self.dl.db.get_cursor()
            cursor.execute("UPDATE positions SET hedge_buddy_id = NULL WHERE hedge_buddy_id = ?", (position_id,))
            self.dl.db.commit()
            cursor.close()
            log.success(f"💣 Cleared hedge_buddy_id for {position_id}", source="PositionCoreService")

            self.dl.delete_position(position_id)
            log.success(f"✅ Deleted position {position_id}", source="PositionCoreService")

        except Exception as ex:
            log.error(f"❌ Error during delete_position_and_cleanup: {ex}", source="PositionCoreService")

    def record_positions_snapshot(self):
        try:
            positions = self.dl.positions.get_active_positions()
            calc = CalculationCore(self.dl)
            totals = calc.calculate_totals(positions)
            self.dl.portfolio.record_snapshot(totals)
            log.success(f"📋 Snapshot of {len(positions)} positions recorded.", source="PositionCoreService")
        except Exception as e:
            log.error(f"❌ record_positions_snapshot failed: {e}", source="PositionCoreService")
