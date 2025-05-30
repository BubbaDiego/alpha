import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.alert import AlertLevel, Condition, AlertType
from utils.fuzzy_wuzzy import fuzzy_match_enum
from core.logging import log
from alert_core.threshold_service import ThresholdService
from data.models import AlertThreshold


class AlertEvaluationService:
    def __init__(self, threshold_service: ThresholdService):
        self.threshold_service = threshold_service
        self.repo = None  # Set via inject_repo()

    def inject_repo(self, repo):
        self.repo = repo

    def evaluate(self, alert):
        try:
            if (
                str(alert.alert_class).strip() == "System"
                and alert.alert_type == AlertType.DeathNail
            ):
                alert.level = AlertLevel.HIGH
                return alert
            if alert.evaluated_value is None:
                log.warning(
                    f"⚠️ Missing evaluated_value for alert {alert.id}; defaulting to 0",
                    source="AlertEvaluation",
                )
                alert.evaluated_value = 0.0

            alert_type = str(alert.alert_type).strip()
            alert_class = str(alert.alert_class).strip()
            condition = str(alert.condition).strip()

            # Optional enum normalization (safety)
            enum_type = fuzzy_match_enum(alert_type.split('.')[-1], AlertType)
            if not enum_type:
                log.warning(f"⚠️ Unable to resolve AlertType enum from: {alert_type}", source="AlertEvaluation")
                return self._evaluate(alert)

            # 🎯 Try dynamic threshold from DB
            threshold = self.threshold_service.get_thresholds(enum_type.value, alert_class, condition)
            if threshold:
                return self._evaluate_against(alert, threshold)

            log.warning(f"⚠️ No DB threshold found → fallback triggered for {alert.id}", source="AlertEvaluation")
            return self._evaluate(alert)

        except Exception as e:
            log.error(f"❌ Evaluation error for alert {alert.id}: {e}", source="AlertEvaluation")
            alert.level = AlertLevel.NORMAL
            return alert

    def _evaluate_against(self, alert, threshold: AlertThreshold):
        val = alert.evaluated_value
        cond = alert.condition

        if cond == Condition.ABOVE:
            if val >= threshold.high:
                level = AlertLevel.HIGH
            elif val >= threshold.medium:
                level = AlertLevel.MEDIUM
            elif val >= threshold.low:
                level = AlertLevel.LOW
            else:
                level = AlertLevel.NORMAL
        elif cond == Condition.BELOW:
            if val <= threshold.high:
                level = AlertLevel.HIGH
            elif val <= threshold.medium:
                level = AlertLevel.MEDIUM
            elif val <= threshold.low:
                level = AlertLevel.LOW
            else:
                level = AlertLevel.NORMAL
        else:
            level = AlertLevel.NORMAL

        alert.level = level
        log.success(f"✅ DB Evaluation: {alert.id} → level={level}", source="AlertEvaluation", payload={
            "evaluated_value": val,
            "low": threshold.low,
            "medium": threshold.medium,
            "high": threshold.high
        })
        return alert

    def _evaluate(self, alert):
        try:
            evaluated = alert.evaluated_value
            trigger = alert.trigger_value
            condition = alert.condition

            log.debug(f"📈 Raw Eval → Value={evaluated}, Trigger={trigger}, Condition={condition}", source="AlertEvaluation")

            if condition == Condition.ABOVE and evaluated >= trigger:
                alert.level = AlertLevel.HIGH
            elif condition == Condition.BELOW and evaluated <= trigger:
                alert.level = AlertLevel.HIGH
            else:
                alert.level = AlertLevel.NORMAL

            log.info(f"ℹ️ Fallback eval for {alert.id} → Level: {alert.level}", source="AlertEvaluation")
            return alert

        except Exception as e:
            log.error(f"❌ Fallback eval error for alert {alert.id}: {e}", source="AlertEvaluation")
            alert.level = AlertLevel.NORMAL
            return alert

    def update_alert_evaluated_value(self, alert_id: str, value: float):
        if not self.repo:
            log.error("❌ Alert repository not injected", source="AlertEvaluation")
            return
        try:
            cursor = self.repo.data_locker.db.get_cursor()
            cursor.execute(
                "UPDATE alerts SET evaluated_value = ? WHERE id = ?", (value, alert_id)
            )
            self.repo.data_locker.db.commit()
            log.success("✅ Updated evaluated_value", source="AlertEvaluation", payload={
                "alert_id": alert_id, "evaluated_value": value
            })
        except Exception as e:
            log.error("❌ Failed to update evaluated_value", source="AlertEvaluation", payload={
                "alert_id": alert_id, "error": str(e)
            })

    def update_alert_level(self, alert_id: str, level):
        if not self.repo:
            log.error("❌ Alert repository not injected", source="AlertEvaluation")
            return
        try:
            level_str = level.value if hasattr(level, "value") else str(level).capitalize()
            cursor = self.repo.data_locker.db.get_cursor()
            cursor.execute(
                "UPDATE alerts SET level = ? WHERE id = ?", (level_str, alert_id)
            )
            self.repo.data_locker.db.commit()
            log.success("🧪 Updated alert level", source="AlertEvaluation", payload={
                "alert_id": alert_id, "level": level_str
            })
        except Exception as e:
            log.error("❌ Failed to update alert level", source="AlertEvaluation", payload={
                "alert_id": alert_id, "error": str(e)
            })
