

from core.logging import log

def log_dashboard_flat(ctx: dict):
    print("✅ log_dashboard_flat invoked")

    log.banner("📦 DASHBOARD STATUS SNAPSHOT")

    totals = ctx.get("totals", {})
    flat_metrics = {
        "theme_mode": ctx.get("theme_mode"),
        "portfolio_value": ctx.get("portfolio_value"),
        "total_value": totals.get("total_value"),
        "total_size": totals.get("total_size"),
        "avg_leverage": totals.get("avg_leverage"),
        "avg_travel_percent": totals.get("avg_travel_percent"),
        "avg_heat_index": totals.get("avg_heat_index"),
    }

    log.info("📊 Core Metrics", source="DashboardContext", payload=flat_metrics)

def log_dashboard_full(ctx: dict):
    log.banner("🧠 FULL DASHBOARD CONTEXT DUMP")

    log.info("🎨 Theme Mode + Portfolio", source="DashboardContext", payload={
        "theme_mode": ctx.get("theme_mode"),
        "portfolio_value": ctx.get("portfolio_value"),
        "portfolio_change": ctx.get("portfolio_change")
    })

    log.info("📦 Totals", source="DashboardContext", payload=ctx.get("totals"))
    log.info("📈 Ledger Info", source="DashboardContext", payload=ctx.get("ledger_info"))
    log.info("🎯 Portfolio Limits", source="DashboardContext", payload=ctx.get("portfolio_limits"))
    log.info("📊 Status Items", source="DashboardContext", payload=ctx.get("status_items", {}))
    log.info("🛠️ Monitor Items", source="DashboardContext", payload=ctx.get("monitor_items", {}))

    # 🧠 Charts + Visual Data (last 3 only)
    graph = ctx.get("graph_data", {})
    trimmed_graph = {
        "timestamps": graph.get("timestamps", [])[-3:],
        "values": graph.get("values", [])[-3:],
        "collateral": graph.get("collateral", [])[-3:]
    }

    log.info("📈 Graph Data (last 3)", source="DashboardContext", payload=trimmed_graph)
    log.info("🥧 Size Composition (LONG/SHORT %)", source="DashboardContext", payload=ctx.get("size_composition", {}))
    log.info("💰 Collateral Composition (LONG/SHORT %)", source="DashboardContext", payload=ctx.get("collateral_composition", {}))

    if ctx.get("positions"):
        sample = ctx["positions"][:3]
        log.debug("📍 Sample Positions (up to 3)", source="DashboardContext", payload=sample)

    log.success("✅ Full dashboard context rendered", source="DashboardContext")

def list_positions_verbose(ctx: dict, limit: int = 10):
    log.banner("📍 POSITION DATA DUMP")

    positions = ctx.get("positions", [])
    if not positions:
        log.warning("No positions available in context.", source="DashboardContext")
        return

    log.info(f"Showing up to {limit} positions...", source="DashboardContext")

    for i, pos in enumerate(positions[:limit]):
        pos_data = {
            "id": pos.get("id", f"#{i}"),
            "asset": pos.get("asset_type"),
            "wallet": pos.get("wallet") or pos.get("wallet_name") or "❓",
            "size": pos.get("size"),
            "collateral": pos.get("collateral"),
            "leverage": pos.get("leverage"),
            "heat": pos.get("heat_index"),
            "type": pos.get("position_type"),
            "liquid_dist": pos.get("liquidation_distance"),
            "travel": pos.get("travel_percent")
        }
        log.debug(f"📦 Position {i + 1}", source="PositionData", payload=pos_data)

    log.success(f"✅ Finished logging {min(len(positions), limit)} position(s).", source="DashboardContext")
