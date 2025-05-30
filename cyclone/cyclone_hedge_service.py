# cyclone/cyclone_hedge_service.py

from hedge_core.hedge_core import HedgeCore
from core.core_imports import log


class CycloneHedgeService:
    def __init__(self, data_locker):
        self.dl = data_locker
        self.core = HedgeCore(self.dl)


    async def update_hedges(self):
        log.info("🔄 Starting Hedge Update", source="CycloneHedge")
        try:
            hedge_groups = self.core.link_hedges()
            log.info(
                f"Found {len(hedge_groups)} hedge group(s)",
                source="CycloneHedge",
            )

            hedges = self.core.build_hedges()
            log.success(
                f"✅ Built {len(hedges)} hedge(s) from {len(self.dl.positions.get_all_positions())} positions",
                source="CycloneHedge",
            )
        except Exception as e:
            log.error(f"❌ Hedge update failed: {e}", source="CycloneHedge")

    async def link_hedges(self):
        log.info("🔗 Linking Hedges", source="CycloneHedge")
        try:
            hedge_groups = self.core.link_hedges()
            log.success(f"✅ Linked {len(hedge_groups)} hedge group(s)", source="CycloneHedge")
        except Exception as e:
            log.error(f"❌ Link Hedges failed: {e}", source="CycloneHedge")
