import os
import sys
import uuid
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.constants import DB_PATH
from data.data_locker import DataLocker
from cyclone.cyclone_engine import Cyclone
from core.logging import log

# ⚙️ Boot up the data layer + Cyclone
dl = DataLocker(str(DB_PATH))
cyclone = Cyclone()

# 🧪 Generate a valid test position
def generate_position_for_enrichment(asset="SOL"):
    return {
    "id": str(uuid.uuid4()),
    "asset_type": "SOL",
    "position_type": "long",
    "entry_price": 100,
    "current_price": 120,
    "liquidation_price": 50,
    "collateral": 500,
    "size": 5.0,
    "leverage": 2.0,
    "value": 2000,
    "pnl_after_fees_usd": 0.0,
    "wallet_name": "TestWallet",
    "last_updated": datetime.now().isoformat(),
    "current_heat_index": 0.0,
    "travel_percent": 0.0,
    "liquidation_distance": 0.0,  # ✅ the one currently failing
}


def test_enrich_positions_through_cyclone():
    log.banner("🧪 TEST: Cyclone Enrichment")

    # Step 1: Clear all positions
    dl.positions.delete_all_positions()
    log.info("🧼 Deleted all existing positions", source="Setup")

    # Step 2: Insert test position
    try:
        pos = generate_position_for_enrichment()
        dl.positions.insert_position(pos)
        log.success("✅ Inserted dummy position for enrichment", source="Setup")
    except Exception as e:
        log.error(f"❌ Failed to insert test position: {e}", source="DLPositionManager")
        return

    # Step 3: Run Cyclone enrichment
    log.info("⚙️ Running cyclone.enrich_positions()", source="Cyclone")
    try:
        enriched = asyncio.run(cyclone.enrich_positions())
        if not enriched:
            log.warning("⚠️ No positions were enriched", source="Cyclone")
        else:
            log.success(f"✅ Cyclone enriched {len(enriched)} position(s)", source="Cyclone")
            log.info("🔍 Enriched Position Result", source="Cyclone", payload={
                k: enriched[0].get(k) for k in [
                    "id", "asset_type", "position_type",
                    "leverage", "travel_percent",
                    "liquidation_distance", "heat_index", "current_price"
                ]
            })
    except Exception as e:
        log.error(f"❌ Enrichment via Cyclone failed: {e}", source="Cyclone")

    log.banner("✅ TEST COMPLETE: test_cyclone_step_enrich_positions")

if __name__ == "__main__":
    test_enrich_positions_through_cyclone()
