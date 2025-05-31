"""Connect Phantom wallet to the Jupiter dApp."""

async def run(engine):
    await engine.pm.connect_wallet(
        dapp_url=engine.dapp_url,
        phantom_password=engine.phantom_password,
    )
