
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
import requests
import time
from core.logging import log
from core.constants import JUPITER_API_BASE
from data.data_locker import DataLocker
from positions.position_enrichment_service import PositionEnrichmentService
from calc_core.calculation_core import CalculationCore

class PositionSyncService:
    def __init__(self, data_locker):
        self.dl = data_locker

    MINT_TO_ASSET = {
        "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh": "BTC",
        "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs": "ETH",
        "So11111111111111111111111111111111111111112": "SOL"
    }

    def _request_with_retries(self, url: str, attempts: int = 3, delay: float = 1.0):
        """Return a requests.Response object with simple retry logic."""
        headers = {"User-Agent": "Cyclone/PositionSyncService"}
        for attempt in range(1, attempts + 1):
            try:
                res = requests.get(url, headers=headers, timeout=10)
                log.debug(
                    f"📡 Attempt {attempt} → status {res.status_code}",
                    source="JupiterAPI",
                )
                res.raise_for_status()
                return res
            except requests.RequestException as e:
                log.error(
                    f"[{attempt}/{attempts}] Request error: {e}",
                    source="JupiterAPI",
                )
                if attempt == attempts:
                    raise
                time.sleep(delay * attempt)

    def run_full_jupiter_sync(self, source="user") -> dict:
        from positions.hedge_manager import HedgeManager
        from data.dl_monitor_ledger import DLMonitorLedgerManager

        try:
            # Step 1: Sync Jupiter Positions
            result = self.update_jupiter_positions()

            if "error" in result:
                log.error(f"❌ Jupiter Sync Failed: {result['error']}", source="PositionSyncService")
                result.update({
                    "success": False,
                    "hedges": 0,
                    "timestamp": datetime.now().isoformat()
                })
                return result

            imported = result.get("imported", 0)
            skipped = result.get("skipped", 0)
            errors = result.get("errors", 0)

            log.success(f"✅ Jupiter positions imported: {imported}", source="PositionSyncService")

            # Step 2: Hedge Generation
            positions = self.dl.positions.get_all_positions()
            hedge_manager = HedgeManager(positions)
            hedges = hedge_manager.get_hedges()
            log.success(f"🌐 HedgeManager created {len(hedges)} hedges", source="PositionSyncService")

            # Step 3: Timestamp & Snapshot
            now = datetime.now()
            self.dl.system.set_last_update_times({
                "last_update_time_positions": now.isoformat(),
                "last_update_positions_source": source,
                "last_update_time_prices": now.isoformat(),
                "last_update_prices_source": source
            })

            calc_core = CalculationCore(self.dl)
            active_positions = self.dl.positions.get_active_positions()
            totals = calc_core.calculate_totals(active_positions)
            self.dl.portfolio.record_snapshot(totals)

            # Step 4: HTML Report
            try:
                base_dir = os.path.abspath(os.path.join(self.dl.db.db_path, "..", ".."))
                reports_dir = os.path.join(base_dir, "reports")
                os.makedirs(reports_dir, exist_ok=True)

                timestamp_str = now.strftime("%Y%m%d_%H%M%S")
                report_filename = f"sync_report_{timestamp_str}.html"
                report_path = os.path.join(reports_dir, report_filename)

                html_content = """..."""  # existing HTML generation

                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                log.success(f"📄 Sync report saved to: {report_path}", source="PositionSyncService")

                # Rotate reports
                report_files = sorted(
                    [f for f in os.listdir(reports_dir) if f.startswith("sync_report_")],
                    reverse=True
                )
                for old_file in report_files[5:]:
                    os.remove(os.path.join(reports_dir, old_file))
                    log.info(f"🧹 Removed old report: {old_file}", source="PositionSyncService")

            except Exception as e:
                log.warning(f"⚠️ Failed to write HTML sync report: {e}", source="PositionSyncService")

            # Step 5: Build response
            result.update({
                "success": True,
                "hedges": len(hedges),
                "timestamp": now.isoformat()
            })

            final_msg = f"Sync complete: {imported} imported, {skipped} skipped, {errors} errors, {len(hedges)} hedges"
            log.info(f"📦 {final_msg}", source="PositionSyncService")

            # ✅ Step 6: Ledger Entry
            try:
                ledger = DLMonitorLedgerManager(self.dl.db)
                status = "Success" if errors == 0 else "Error"
                ledger.insert_ledger_entry("position_monitor", status, metadata=result)
            except Exception as e:
                log.warning(f"⚠️ Failed to write monitor ledger: {e}", source="PositionSyncService")

            return result

        except Exception as e:
            log.error(f"❌ run_full_jupiter_sync failed: {e}", source="PositionSyncService")
            return {
                "success": False,
                "error": str(e),
                "imported": 0,
                "skipped": 0,
                "errors": 1,
                "hedges": 0,
                "timestamp": datetime.now().isoformat()
            }

    def update_jupiter_positions(self):
        from positions.position_enrichment_service import PositionEnrichmentService
        from core.logging import log

        log.info("🔄 Updating positions from Jupiter...", source="PositionSyncService")
        try:
            log.info(f"📁 Writing to DB: {self.dl.db.db_path}", source="PositionSyncService")

            wallets = self.dl.read_wallets()
            log.info(f"🔍 Loaded {len(wallets)} wallets for sync", source="PositionSyncService")

            new_positions = []
            errors = 0
            imported = 0
            skipped = 0

            for wallet in wallets:
                pub = wallet.get("public_address", "").strip()
                name = wallet.get("name", "Unnamed")

                if not pub:
                    log.warning(f"⚠️ Skipping {name} — missing address", source="PositionSyncService")
                    continue

                try:
                    url = f"{JUPITER_API_BASE}/v1/positions?walletAddress={pub}&showTpslRequests=true"
                    res = self._request_with_retries(url)

                    log.debug(f"🌐 [{name}] Jupiter API status: {res.status_code}", source="JupiterAPI")
                    log.debug(f"📝 Response Body:\n{res.text}", source="JupiterAPI")

                    data_list = res.json().get("dataList", [])
                    log.info(f"📊 {name} → {len(data_list)} Jupiter positions", source="PositionSyncService")

                    for item in data_list:
                        pos_id = item.get("positionPubkey")
                        if not pos_id:
                            log.warning("🚫 Missing positionPubkey, skipping", source="PositionSyncService")
                            continue

                        raw_pos = {
                            "id": pos_id,
                            "asset_type": self.MINT_TO_ASSET.get(item.get("marketMint", ""), "BTC"),
                            "position_type": item.get("side", "short").lower(),
                            "entry_price": float(item.get("entryPrice", 0.0)),
                            "liquidation_price": float(item.get("liquidationPrice", 0.0)),
                            "collateral": float(item.get("collateral", 0.0)),
                            "size": float(item.get("size", 0.0)),
                            "leverage": float(item.get("leverage", 0.0)),
                            "value": float(item.get("value", 0.0)),
                            "last_updated": datetime.fromtimestamp(float(item.get("updatedTime", 0))).isoformat(),
                            "wallet_name": name,
                            "pnl_after_fees_usd": float(item.get("pnlAfterFeesUsd", 0.0)),
                            "travel_percent": float(item.get("pnlChangePctAfterFees", 0.0)),
                            "current_price": float(item.get("markPrice", 0.0))
                        }

                        log.debug(f"🆕 Parsed Jupiter position: {raw_pos}", source="Parser")
                        new_positions.append(raw_pos)

                except requests.RequestException as e:
                    log.error(f"❌ [{name}] API Request Error: {e}", source="JupiterAPI")
                    log.debug(f"📝 Raw body:\n{res.text if 'res' in locals() else 'no response'}", source="JupiterAPI")
                    errors += 1

            enricher = PositionEnrichmentService(self.dl)

            # ✅ Fetch DB schema for safe field filtering
            try:
                cursor = self.dl.db.get_cursor()
                cursor.execute("PRAGMA table_info(positions);")
                db_columns = set(row[1] for row in cursor.fetchall())
                cursor.close()
            except Exception as e:
                log.warning(f"⚠️ Failed to fetch DB schema: {e}", source="InsertCheck")
                db_columns = None

            for pos in new_positions:
                try:
                    cursor = self.dl.db.get_cursor()
                    cursor.execute("SELECT COUNT(*) FROM positions WHERE id = ?", (pos["id"],))
                    exists = cursor.fetchone()[0]
                    cursor.close()
                except Exception as e:
                    log.error(f"❌ DB existence check failed for {pos['id']}: {e}", source="InsertCheck")
                    errors += 1
                    continue

                if exists:
                    log.info(f"⏭️ Skipped (already exists): {pos['id']}", source="InsertCheck")
                    skipped += 1
                    continue

                try:
                    enriched = enricher.enrich(pos)
                    enriched.setdefault("alert_reference_id", None)
                    enriched.setdefault("hedge_buddy_id", None)

                    # ✅ Strip unknown fields
                    if db_columns:
                        stripped_keys = set(enriched.keys()) - db_columns
                        if stripped_keys:
                            log.debug(f"🧹 Stripped non-schema keys: {stripped_keys}", source="InsertSanitizer")
                        enriched = {k: v for k, v in enriched.items() if k in db_columns}

                except Exception as e:
                    log.error(f"❌ Enrichment failed for {pos['id']}: {e}", source="Enrichment")
                    errors += 1
                    continue

                try:
                    self.dl.positions.create_position(enriched)
                    log.success(f"✅ Inserted: {pos['id']}", source="InsertVerify")
                    imported += 1
                except Exception as e:
                    log.error(f"❌ Insert failed for {pos['id']}: {e}", source="InsertVerify")
                    errors += 1

            log.info(
                f"📦 Jupiter Sync Result → Imported: {imported}, Skipped: {skipped}, Errors: {errors}",
                source="SyncSummary"
            )

            return {
                "message": "Jupiter sync complete",
                "imported": imported,
                "skipped": skipped,
                "errors": errors
            }

        except Exception as e:
            log.critical(f"💥 Jupiter sync crashed: {e}", source="PositionSyncService")
            return {"error": str(e)}



