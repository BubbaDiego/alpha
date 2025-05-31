from rich.prompt import Prompt

async def connect_wallet(engine):
    """Connect the Phantom wallet to Jupiter."""
    await engine.pm.connect_wallet(
        dapp_url=engine.dapp_url,
        phantom_password=engine.phantom_password,
    )

async def unlock_wallet(engine):
    """Unlock the Phantom wallet using the stored password."""
    if engine.phantom_password:
        await engine.pm.unlock_phantom(engine.phantom_password)

async def select_position_type(engine):
    """Prompt for Long/Short and select the position type via JupiterPerpsFlow."""
    choice = Prompt.ask("Choose position type", choices=["long", "short"], default="long")
    engine.jp.select_position_type(choice)
