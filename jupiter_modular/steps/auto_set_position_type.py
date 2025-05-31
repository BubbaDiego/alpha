"""Select a LONG position type via JupiterPerpsFlow."""

async def run(engine):
    await engine.jp.select_position_type("long")
