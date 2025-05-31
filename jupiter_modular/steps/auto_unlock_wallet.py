"""Unlock Phantom wallet using the engine's stored password."""

async def run(engine):
    if engine.phantom_password:
        await engine.pm.unlock_phantom(engine.phantom_password)
