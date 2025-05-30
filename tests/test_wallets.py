import os
import sys
import types
import importlib
import sqlite3
import logging

# Set up dedicated test DB
TEST_DB = "/tmp/test_wallet.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

# Ensure modules use our DB path
os.environ["DB_PATH"] = TEST_DB

# Stub out heavy logging dependencies
rich_logger_stub = types.ModuleType("utils.rich_logger")
class RichLogger:
    def __getattr__(self, _):
        def no_op(*a, **k):
            pass
        return no_op
class ModuleFilter(logging.Filter):
    def filter(self, record):
        return True
rich_logger_stub.RichLogger = RichLogger
rich_logger_stub.ModuleFilter = ModuleFilter
sys.modules["utils.rich_logger"] = rich_logger_stub
sys.modules["winsound"] = types.ModuleType("winsound")

import core.constants as const
import core.core_imports as ci
const.DB_PATH = TEST_DB
ci.DB_PATH = TEST_DB

import wallets.wallet_repository as wr
import wallets.wallet_service as ws
importlib.reload(wr)
importlib.reload(ws)

from wallets.wallet_service import WalletService
from wallets.wallet_schema import WalletIn
from wallets.encryption import decrypt_key


def setup_service():
    os.environ["WALLET_ENCRYPTION_KEY"] = "sixteenbytekey!!"
    return WalletService()


def test_create_wallet_encrypted(tmp_path):
    service = setup_service()
    data = WalletIn(
        name="test",
        public_address="0xabc",
        private_address="secret",
    )

    service.create_wallet(data)

    conn = sqlite3.connect(TEST_DB)
    row = conn.execute("SELECT private_address FROM wallets WHERE name=?", ("test",)).fetchone()
    assert row is not None
    assert row[0] != "secret"
    assert decrypt_key(row[0]) == "secret"


def test_list_wallet_plaintext_private_key(tmp_path):
    service = setup_service()

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO wallets (name, public_address, private_address, image_path, balance, tags, is_active, type)
        VALUES (?, ?, ?, ?, ?, '', 1, 'personal')
        """,
        ("plain", "0x123", "plaintext", "", 0.0),
    )
    conn.commit()

    wallets = service.list_wallets()
    names = [w.name for w in wallets]
    assert "plain" in names
