#!/usr/bin/env python3
"""Insert or update wallet records from a JSON file.

By default this script loads ``data/wallet_backup.json`` at the repository root.
Pass ``--json /path/to/file`` to specify a different file.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List, Tuple, Optional

# Ensure repository root is on the import path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.core_imports import DB_PATH, configure_console_log
from data.data_locker import DataLocker
from wallets.wallet_service import WalletService
from wallets.wallet_schema import WalletIn


def load_wallets(json_path: Path) -> List[dict]:
    """Load wallet definitions from ``json_path``."""
    with json_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, Iterable):
        raise ValueError("Wallet JSON must contain a list of objects")
    return list(data)


def upsert_wallets(wallets: List[dict], service: WalletService) -> Tuple[int, int]:
    """Create or update wallets via ``service``.

    Returns a tuple ``(created, updated)``.
    """
    created = 0
    updated = 0
    for raw in wallets:
        try:
            wallet = WalletIn(**raw)
        except Exception as exc:  # pragma: no cover - depends on input validity
            print(f"❌ Skipping invalid wallet {raw.get('name')}: {exc}")
            continue

        try:
            if service.repo.get_wallet_by_name(wallet.name):
                service.update_wallet(wallet.name, wallet)
                updated += 1
                print(f"🔄 Updated wallet: {wallet.name}")
            else:
                service.create_wallet(wallet)
                created += 1
                print(f"✅ Inserted wallet: {wallet.name}")
        except Exception as exc:
            print(f"❌ Failed to upsert {wallet.name}: {exc}")
    return created, updated


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Insert or update wallets")
    default_json = REPO_ROOT / "data" / "wallet_backup.json"
    parser.add_argument("--json", default=default_json, type=Path, help="Path to wallet JSON file")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    configure_console_log()

    if not args.json.exists():
        print(f"⚠️ JSON file not found: {args.json}")
        return 1

    wallets = load_wallets(args.json)
    dl = DataLocker(str(DB_PATH))
    service = WalletService()
    created, updated = upsert_wallets(wallets, service)
    dl.close()

    print(f"✅ Completed → {created} created, {updated} updated")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
