# alerts/core.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from alert_core.alert_enrichment_service import AlertEnrichmentService
from alert_core.alert_evaluation_service import AlertEvaluationService
from alert_core.threshold_service import ThresholdService
from alert_core.alert_store import AlertStore
from alert_core.alert_notifier import AlertNotifier
from data.alert import NotificationType
from core.core_imports import log

class AlertCore:
    def __init__(self, data_locker, config_loader=None):
        self.data_locker = data_locker
        def strict_config_loader():
            config = self.data_locker.system.get_var("alert_thresholds")
            if config is None:
                raise RuntimeError("🛑 No alert_thresholds config found in DB")
            return config

        self.config_loader = config_loader or strict_config_loader
        self.repo = AlertStore(data_locker, self.config_loader)
        self.enricher = AlertEnrichmentService(data_locker)
        threshold_service = ThresholdService(data_locker.db)
        self.evaluator = AlertEvaluationService(threshold_service)
        self.alert_store = AlertStore(data_locker, self.config_loader)
        self.evaluator.inject_repo(self.repo)  # ⚡️ enable DB updates

    async def create_alert(self, alert_dict: dict) -> bool:
        try:
            success = self.repo.create_alert(alert_dict)
            if success:
                log.success("✅ AlertCore created alert", source="AlertCore", payload={"id": alert_dict.get("id")})
            return success
        except Exception as e:
            log.error("💥 Failed to create alert", source="AlertCore", payload={"error": str(e)})
            return False

    async def run_alert_evaluation(self):
        log.banner("🚨 Alert Evaluation Triggered")
        return await self.process_alerts()

    async def evaluate_alert(self, alert):
        try:
            enriched = await self.enricher.enrich(alert)
            evaluated = self.evaluator.evaluate(enriched)

            self.evaluator.update_alert_level(evaluated.id, evaluated.level)
            self.evaluator.update_alert_evaluated_value(evaluated.id, evaluated.evaluated_value)

            log.success(
                "🧠 Alert processed",
                source="AlertCore",
                payload={"id": evaluated.id, "level": evaluated.level, "value": evaluated.evaluated_value}
            )

            if evaluated.notification_type == NotificationType.SMS:
                try:
                    notifier = AlertNotifier(self.data_locker)
                    notifier.notify(evaluated)
                except Exception as notify_err:
                    log.error(
                        f"Failed to send SMS notification: {notify_err}",
                        source="AlertCore",
                    )

            return evaluated
        except Exception as e:
            log.error("❌ Failed to evaluate alert", source="AlertCore", payload={"id": alert.id, "error": str(e)})
            return alert

    async def evaluate_all_alerts(self):
        log.banner("🚨 EVALUATING ALL ALERTS")

        alerts = self.repo.get_active_alerts()
        if not alerts:
            log.warning("⚠️ No active alerts found", source="AlertCore")
            return []

        log.info(f"📥 Loaded {len(alerts)} active alerts", source="AlertCore")

        from asyncio import gather
        enriched = await self.enricher.enrich_all(alerts)
        results = await gather(*(self.evaluate_alert(alert) for alert in enriched))

        log.success(f"✅ Finished processing {len(results)} alerts", source="AlertCore")
        return results

    def clear_stale_alerts(self):
        log.banner("🧹 CLEARING STALE ALERTS")

        alerts = self.repo.get_alerts()
        positions = self.data_locker.positions.get_all_positions()
        valid_pos_ids = {p["id"] for p in positions}
        deleted = 0

        for alert in alerts:
            pos_id = alert.get("position_reference_id")
            if pos_id and pos_id not in valid_pos_ids:
                if self.repo.delete_alert(alert["id"]):
                    deleted += 1
                    log.info(
                        "🗑 Deleted dangling alert",
                        source="AlertCore",
                        payload={"alert_id": alert["id"], "missing_position": pos_id}
                    )

        log.success(f"✅ Cleared {deleted} stale alerts", source="AlertCore")
        return deleted

    async def enrich_and_evaluate_alerts(self, alerts: list):
        if not alerts:
            log.warning("⚠️ No alerts to process in enrich_and_evaluate_alerts()", source="AlertCore")
            return []

        log.info(f"🧠 Enriching + Evaluating {len(alerts)} alerts", source="AlertCore")

        enriched = await self.enricher.enrich_all(alerts)
        results = []

        for alert in enriched:
            try:
                evaluated = self.evaluator.evaluate(alert)
                self.evaluator.update_alert_level(evaluated.id, evaluated.level)
                self.evaluator.update_alert_evaluated_value(evaluated.id, evaluated.evaluated_value)

                results.append(evaluated)

                log.debug(
                    f"✅ Evaluated Alert {evaluated.id}",
                    source="AlertCore",
                    payload={"level": evaluated.level, "value": evaluated.evaluated_value}
                )

            except Exception as e:
                log.error(
                    f"❌ Failed to evaluate alert {alert.id}",
                    source="AlertCore",
                    payload={"error": str(e)}
                )

        log.success(f"✅ Completed enrich+evaluate for {len(results)} alerts", source="AlertCore")
        return results

    async def process_alerts(self):
        log.banner("🔍 Processing Alerts: Enrich + Evaluate")

        alerts = self.repo.get_active_alerts()
        if not alerts:
            log.warning("⚠️ No active alerts found", source="AlertCore")
            return []

        evaluated_alerts = await self.enrich_and_evaluate_alerts(alerts)
        return evaluated_alerts

    def create_position_alerts(self):
        self.alert_store.create_position_alerts()

    def create_portfolio_alerts(self):
        self.alert_store.create_portfolio_alerts()

    def create_global_alerts(self):
        self.alert_store.create_global_alerts()

    async def create_all_alerts(self):
        log.banner("🛠 Starting Full Alert Creation")

        try:
            log.start_timer("create_all_alerts")

            # create_portfolio_alerts and create_position_alerts are
            # synchronous methods, so they should not be awaited.
            self.create_portfolio_alerts()
            self.create_position_alerts()

            log.end_timer("create_all_alerts", source="AlertCore")
            log.success("🛠 Alert generation complete", source="AlertCore")

        except Exception as e:
            log.error(f"❌ Failed in create_all_alerts: {e}", source="AlertCore")


    async def enrich_all_alerts(self):
        """
        Runs enrichment only — no evaluation or notification.
        """
        log.banner("💡 Enriching All Alerts")

        try:
            alerts = self.repo.get_active_alerts()
            if not alerts:
                log.warning("⚠️ No active alerts to enrich", source="AlertCore")
                return []

            log.info(f"📥 Loaded {len(alerts)} alerts", source="AlertCore")
            enriched = await self.enricher.enrich_all(alerts)

            log.success("✅ Alert enrichment complete", source="AlertCore", payload={"count": len(enriched)})
            return enriched

        except Exception as e:
            log.error(f"❌ enrich_all_alerts() failed: {e}", source="AlertCore")
            return []

    async def update_evaluated_values(self):
        """
        Evaluates alerts and updates only their evaluated_value (no notify).
        """
        log.banner("🧪 Updating Evaluated Values")

        try:
            alerts = self.repo.get_active_alerts()
            if not alerts:
                log.warning("⚠️ No active alerts to update", source="AlertCore")
                return

            enriched = await self.enricher.enrich_all(alerts)
            for alert in enriched:
                try:
                    evaluated = self.evaluator.evaluate(alert)
                    self.evaluator.update_alert_evaluated_value(evaluated.id, evaluated.evaluated_value)
                    log.success("✅ Updated evaluated_value", source="AlertCore", payload={
                        "id": evaluated.id,
                        "value": evaluated.evaluated_value
                    })
                except Exception as e:
                    log.error(f"❌ Failed to update value for alert {alert.id}: {e}", source="AlertCore")

            log.success("✅ Completed evaluated value update", source="AlertCore")

        except Exception as e:
            log.error(f"💥 update_evaluated_values() failed: {e}", source="AlertCore")
