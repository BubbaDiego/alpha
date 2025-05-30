# cyclone_position_service.py
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timezone
from uuid import uuid4
import asyncio
import os

from data.data_locker import DataLocker
from positions.position_core_service import PositionCoreService
from positions.position_sync_service import PositionSyncService
from monitor.monitor_utils import LedgerWriter
from data.alert import AlertType, Condition
from core.logging import log
from alert_core.alert_utils import log_alert_summary
from core.constants import DB_PATH

print("👁 Viewer using DB path:", os.path.abspath(DB_PATH))

def validate_position_service_source():
    """Helper for debugging where PositionCore is loaded from."""
    import inspect
    from positions.position_core import PositionCore

    print("📂 [Validator] PositionCore loaded from:", inspect.getfile(PositionCore))
    print(
        "🔍 Has method update_positions_from_jupiter():",
        hasattr(PositionCore, "update_positions_from_jupiter"),
    )


class CyclonePositionService:
    def __init__(self, data_locker):
        self.dl = data_locker

    def update_positions_from_jupiter(self):
        from positions.position_sync_service import PositionSyncService

        print("🛰️ [TRACE] CyclonePositionService.update_positions_from_jupiter() CALLED")

        try:
            sync_service = PositionSyncService(self.dl)
            sync_service.update_jupiter_positions()
        except Exception as e:
            print(f"❌ ERROR while calling update_jupiter_positions: {e}")

    async def enrich_positions(self):
        log.info("✨ Starting Position Enrichment", source="CyclonePosition")
        try:
            from positions.position_core import PositionCore
            core = PositionCore(self.dl)
            enriched = await core.enrich_positions()
            count = len(enriched)
            log.success(f"✅ Enriched {count} positions", source="CyclonePosition")
            print(f"🔍 Enriched {count} positions.")
        except Exception as e:
            log.error(f"❌ Position enrichment failed: {e}", source="CyclonePosition")

    async def delete_position(self, position_id: str):
        try:
            await asyncio.to_thread(self.dl.positions.delete_position, position_id)
            log.warning(f"🧹 Deleted position: {position_id}", source="CyclonePosition")
        except Exception as e:
            log.error(f"❌ Failed to delete position: {e}", source="CyclonePosition")

    async def clear_positions_backend(self):
        try:
            await asyncio.to_thread(self.dl.positions.clear_positions)
            log.success("🧹 All positions cleared.", source="CyclonePosition")
        except Exception as e:
            log.error(f"❌ Failed to clear positions: {e}", source="CyclonePosition")

    async def link_hedges(self):
        log.info("🛡 Finding hedge candidates...", source="CyclonePosition")
        try:
            from positions.position_core import PositionCore
            core = PositionCore(self.dl)
            await asyncio.to_thread(core.link_hedges)
            log.success("✅ Hedges linked.", source="CyclonePosition")
        except Exception as e:
            log.error(f"❌ Failed to link hedges: {e}", source="CyclonePosition")

    def view_positions(self):
        """
        CLI viewer for positions — dynamically reloads from DB.
        """
        try:
            index = 0

            while True:
                positions = self.dl.positions.get_all_positions()

                if not positions:
                    os.system("cls" if os.name == "nt" else "clear")
                    print("⚠️ No positions found.\n")
                    break

                total = len(positions)

                if index >= total:
                    index = 0

                os.system("cls" if os.name == "nt" else "clear")
                pos = positions[index]

                print("━━━━━━━━━━ POSITION ━━━━━━━━━━")
                print(f"🆔 ID:           {pos.get('id', '')}")
                print(f"💰 Asset:        {pos.get('asset_type', '')}")
                print(f"📉 Type:         {pos.get('position_type', '')}")
                print(f"📈 Entry Price:  {pos.get('entry_price', '')}")
                print(f"🔄 Current:      {pos.get('current_price', '')}")
                print(f"💣 Liq. Price:   {pos.get('liquidation_price', '')}")
                print(f"🪙 Collateral:   {pos.get('collateral', '')}")
                print(f"📦 Size:         {pos.get('size', '')}")
                print(f"⚖ Leverage:     {pos.get('leverage', '')}x")
                print(f"💵 Value:        {pos.get('value', '')}")
                print(f"💰 PnL (net):    {pos.get('pnl_after_fees_usd', '')}")
                print(f"💼 Wallet:       {pos.get('wallet_name', '')}")
                print(f"🧠 Alert Ref:    {pos.get('alert_reference_id', '')}")
                print(f"🛡 Hedge ID:     {pos.get('hedge_buddy_id', '')}")
                print(f"📅 Updated:      {pos.get('last_updated', '')}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

                print(f"📘 Page {index + 1} of {total}")
                print("Commands: [N]ext | [P]rev | [Q]uit | [Enter]=Next/Quit")
                cmd = input("→ ").strip().lower()
                if cmd == "q":
                    break
                elif cmd == "p":
                    index = (index - 1) % total
                else:
                    index = (index + 1) % total

        except Exception as e:
            log.error(f"❌ Failed to view positions: {e}", source="CyclonePosition")

