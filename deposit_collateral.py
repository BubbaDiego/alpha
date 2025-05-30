from auto_core import AutoCore
from pathlib import Path

if __name__ == "__main__":
    # Default Phantom extension path bundled with this repo. Override if needed.
    PHANTOM_PATH = str(Path(__file__).resolve().parent / "wallets" / "phantom_wallet")
    PROFILE_DIR = "/absolute/path/to/persistent/profile"

    core = AutoCore(
        phantom_path=PHANTOM_PATH,
        profile_dir=PROFILE_DIR,
        headless=False,
        slow_mo=100,
    )

    AMOUNT = 5.0  # Replace with test amount
    core.deposit_collateral(amount=AMOUNT)
