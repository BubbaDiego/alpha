
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.fuzzy_wuzzy import fuzzy_match_enum
from data.alert import AlertType
from utils.json_manager import JsonManager  # ensure this is at the top
import asyncio
import re
from utils.travel_percent_logger import log_travel_percent_comparison
from calc_core.calculation_core import CalculationCore
from alert_core.alert_utils import normalize_alert_fields
from data.alert import AlertType
from core.logging import log



class AlertEnrichmentService:
    def __init__(self, data_locker, system_core=None):
        self.data_locker = data_locker
        self.core = CalculationCore(data_locker)
        self.calc_services = self.core.calc_services
        self.system_core = system_core

    async def enrich(self, alert):
        """
        Enrich the alert based on its alert_class.
        Dispatches to portfolio, position, or market enrichment as needed.
        """
        try:
            if not alert:
                log.error("❌ Enrichment failed: alert is None", source="AlertEnrichment")
                return alert

            if not alert.alert_class:
                log.warning(f"⚠️ Skipping enrichment: missing alert_class on {alert.id}", source="AlertEnrichment")
                return alert

            if not alert.alert_type:
                log.warning(f"⚠️ Skipping enrichment: missing alert_type on {alert.id}", source="AlertEnrichment")
                return alert

            normalize_alert_fields(alert)

            if alert.alert_class == "Portfolio":
                log.debug(f"🚦 Portfolio enrichment dispatched for alert {alert.id}", source="AlertEnrichment")
                return await self._enrich_portfolio(alert)

            elif alert.alert_class == "Position":
                return await self._enrich_position_type(alert)

            elif alert.alert_class == "Market":
                return await self._enrich_price_threshold(alert)

            elif alert.alert_class == "System":
                return await self._enrich_system(alert)

            else:
                log.warning(f"⚠️ Unknown alert_class '{alert.alert_class}' for alert {alert.id}",
                            source="AlertEnrichment")
                return alert

        except Exception as e:
            log.error(f"❌ Exception during enrichment of alert {alert.id}: {e}", source="AlertEnrichment")
            return alert

    async def _enrich_portfolio(self, alert):
        try:
            # Simplified enrichment for test environment
            alert.evaluated_value = 0.0
            log.debug("Portfolio enrichment stub", source="AlertEnrichment")
            return alert

        except Exception as e:
            log.error(f"❌ Portfolio enrichment failed for alert {alert.id}: {e}", source="AlertEnrichment")
            return alert

    async def _enrich_position_type(self, alert):
        try:
            #alert_type_enum = fuzzy_match_enum(str(alert.alert_type), AlertType)

            raw_type = str(alert.alert_type)
            cleaned = raw_type.split('.')[-1]  # Strip enum wrapper
            alert_type_enum = fuzzy_match_enum(cleaned, AlertType)

            if not alert_type_enum:
                log.warning(f"⚠️ Unable to fuzzy-match alert type: {alert.alert_type}", source="AlertEnrichment")
                return alert

            alert.alert_type = alert_type_enum
            alert_type_str = alert_type_enum.name.lower()
            log.debug(f"📌 Matched alert type: {alert_type_str}", source="AlertEnrichment")

            if alert_type_str == "profit":
                log.debug(f"🧭 Routing to _enrich_profit for alert {alert.id}", source="AlertEnrichment")
                return await self._enrich_profit(alert)
            elif alert_type_str == "heatindex":
                log.debug(f"🧭 Routing to _enrich_heat_index for alert {alert.id}", source="AlertEnrichment")
                return await self._enrich_heat_index(alert)
            elif alert_type_str == "travelpercentliquid":
                log.debug(f"🧭 Routing to _enrich_travel_percent for alert {alert.id}", source="AlertEnrichment")
                return await self._enrich_travel_percent(alert)
            else:
                log.warning(f"⚠️ Unsupported matched alert type: {alert_type_str}", source="AlertEnrichment")
                return alert

        except Exception as e:
            log.error(f"❌ Fuzzy match error during enrichment of alert {alert.id}: {e}", source="AlertEnrichment")
            return alert

    async def _enrich_travel_percent(self, alert):
        from utils.travel_percent_logger import log_travel_percent_comparison

        try:
            position = self.data_locker.get_position_by_reference_id(alert.position_reference_id)
            if not position:
                log.error(f"Position not found for alert {alert.id}", source="AlertEnrichment")
                return alert

            entry_price = position.get("entry_price")
            liquidation_price = position.get("liquidation_price")
            position_type = position.get("position_type")

            if not all([entry_price, liquidation_price, position_type]):
                alert.notes = (alert.notes or "") + " 🔸 TravelPercent defaulted due to missing price fields.\n"
                alert.evaluated_value = 0.0
                log.warning(f"⚠️ TravelPercent inputs missing for alert {alert.id}. Using default 0.0",
                            source="AlertEnrichment")
                return alert

            current_price_data = self.data_locker.get_latest_price(position.get("asset_type"))
            if not current_price_data:
                alert.notes = (alert.notes or "") + " 🔸 TravelPercent defaulted due to missing market price.\n"
                alert.evaluated_value = 0.0
                log.warning(f"⚠️ Market price not found for asset {position.get('asset_type')} → defaulting",
                            source="AlertEnrichment")
                return alert

            current_price = current_price_data.get("current_price")

            travel_percent = self.calc_services.calculate_travel_percent(
                position_type=position_type,
                entry_price=entry_price,
                current_price=current_price,
                liquidation_price=liquidation_price
            )

            # Jupiter-provided travel_percent (simulated from position data)
            jupiter_value = 43.5#position.get("travel_percent")

            log.info(f"🛰 Logging drift | Jupiter={jupiter_value}", source="TravelLogger")

            if jupiter_value is not None:
                log_travel_percent_comparison(
                    alert_id=alert.id,
                    jupiter_value=jupiter_value,
                    calculated_value=travel_percent,
                    format="csv"
                )

            if travel_percent is None:
                travel_percent = 0.0
                alert.notes = (alert.notes or "") + " 🔸 TravelPercent calc returned None → defaulted.\n"
                log.warning(f"⚠️ Travel calc failed for alert {alert.id} → default 0.0", source="AlertEnrichment")
            else:
                log.success(f"✅ Enriched Travel Percent Alert {alert.id} evaluated_value={travel_percent}",
                            source="AlertEnrichment")

            alert.evaluated_value = travel_percent

            # ✅ Inject wallet
            wallet_name = position.get("wallet_name")
            wallet = self.data_locker.get_wallet_by_name(wallet_name) if wallet_name else None
            return alert

        except Exception as e:
            log.error(f"Error enriching Travel Percent for alert {alert.id}: {e}", source="AlertEnrichment")
            alert.evaluated_value = 0.0
            alert.notes = (alert.notes or "") + " 🔸 TravelPercent exception → defaulted.\n"
            return alert

    async def _enrich_price_threshold(self, alert):
        current_price_data = self.data_locker.get_latest_price(alert.asset)
        if not current_price_data:
            log.error(f"Current price not found for asset {alert.asset}", source="AlertEnrichment")
            return alert
        alert.evaluated_value = current_price_data.get("current_price")
        log.success(f"✅ Enriched PriceThreshold Alert {alert.id} evaluated_value={alert.evaluated_value}", source="AlertEnrichment")
        return alert

    async def _enrich_profit(self, alert):
        position = self.data_locker.get_position_by_reference_id(alert.position_reference_id)
        if not position:
            log.error(f"Position not found for alert {alert.id}", source="AlertEnrichment")
            return alert

        pnl = position.get("pnl_after_fees_usd") or 0.0
        alert.evaluated_value = pnl

        # ✅ Inject wallet metadata
        wallet_name = position.get("wallet_name")
        wallet = self.data_locker.get_wallet_by_name(wallet_name) if wallet_name else None
        log.success(f"✅ Enriched Profit Alert {alert.id} → {pnl}", source="AlertEnrichment")
        return alert

    async def _enrich_heat_index(self, alert):
        position = self.data_locker.get_position_by_reference_id(alert.position_reference_id)
        if not position:
            log.error(f"Position not found for alert {alert.id}", source="AlertEnrichment")
            return alert

        heat = position.get("current_heat_index")

        if heat is None:
            heat = 5.0  # ← ✅ Default fallback value
            alert.notes = (alert.notes or "") + " 🔸 Default heat index applied (5.0).\n"
            log.warning(f"⚠️ No heat_index for position {position.get('id')} on alert {alert.id} → using default 5.0",
                        source="AlertEnrichment")
        else:
            log.success(f"✅ Enriched HeatIndex Alert {alert.id} evaluated_value={heat}", source="AlertEnrichment")

        # ✅ Inject wallet
        wallet_name = position.get("wallet_name")
        wallet = self.data_locker.get_wallet_by_name(wallet_name) if wallet_name else None
        alert.evaluated_value = heat
        return alert

    async def _enrich_system(self, alert):
        """Simple system alert enrichment."""
        alert.evaluated_value = 1.0
        return alert

    async def enrich_all(self, alerts):
        """
        Asynchronously enrich a list of alerts using asyncio.gather.
        Returns a list of enriched alerts.
        """
        if not isinstance(alerts, list):
            log.error("❌ enrich_all() expected a list of alerts", source="AlertEnrichment")
            return []

        log.info(f"🚀 Starting enrichment for {len(alerts)} alerts", source="AlertEnrichment")

        # 🧠 Normalize all alerts before enriching
        alerts = [normalize_alert_fields(alert) for alert in alerts]

        enriched_alerts = await asyncio.gather(*(self.enrich(alert) for alert in alerts))

        log.success(f"✅ Enriched {len(enriched_alerts)} alerts", source="AlertEnrichment")
        return enriched_alerts

