# Jupiter Core Modular Engine

This folder contains a minimal async automation framework used for the Jupiter
playground.  Steps live in `jupiter_core/steps` and are loaded dynamically by
`jupiter_core/jupiter_modular_console.py`.

## Adding Steps

1. Create a file in `jupiter_core/steps` named `auto_<name>.py`.
2. Implement an `async def run(engine)` function that performs your actions using
   `engine.pm` (the `PhantomManager`) or `engine.jp` (the `JupiterPerpsFlow`).
3. When the console runs it will automatically pick up the new module.

## Running the Console

```bash
python -m jupiter_core.jupiter_modular_console
```

Select a step number from the menu and it will be executed in the launched
browser context.  The sample steps demonstrate wallet connection,
unlocking and setting a position type.
