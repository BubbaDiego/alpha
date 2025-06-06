"""
Author: BubbaDiego
Module: constants.py
Description:
    Central config for environment paths, file locations, image assets,
    and blockchain contract settings. Auto-resolves platform-specific paths
    and supports environment variable overrides.
"""

import os
import sys
from pathlib import Path

# -----------------------------
# 🧠 Cross-platform date format
# -----------------------------
LOG_DATE_FORMAT = "%#m-%#d-%y : %#I:%M:%S %p %Z" if sys.platform.startswith('win') else "%-m-%-d-%y : %-I:%M:%S %p %Z"

# -----------------------------
# 📦 Base Directory & Structure
# -----------------------------
BASE_DIR = Path(os.getenv("BASE_DIR", Path(__file__).resolve().parent.parent))

DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
LOG_DIR = BASE_DIR / "logs"
IMAGE_DIR = BASE_DIR / "images"
MONITOR_DIR = BASE_DIR / "monitor"

# -----------------------------
# 📁 Core File Paths
# -----------------------------
DB_FILENAME = os.getenv("DB_FILENAME", "mother_brain.db")
DB_PATH = DATA_DIR / DB_FILENAME

CONFIG_PATH = CONFIG_DIR / os.getenv("CONFIG_FILENAME", "sonic_config.json")
ALERT_THRESHOLDS_PATH = CONFIG_DIR / os.getenv("ALERT_THRESHOLDS_FILENAME", "alert_thresholds.json")
SONIC_SAUCE_PATH = CONFIG_DIR / os.getenv("SONIC_SAUCE_FILENAME", "sonic_sauce.json")
COM_CONFIG_PATH = CONFIG_DIR / os.getenv("COM_CONFIG_FILENAME", "com_config.json")
THEME_CONFIG_PATH = CONFIG_DIR / os.getenv("THEME_CONFIG_FILENAME", "theme_config.json")
PERPETUAL_TOKENS_PATH = CONFIG_DIR / os.getenv("PERPETUAL_TOKENS_FILENAME", "perpetual_tokens.json")

# Optional heartbeat file location
HEARTBEAT_FILE = Path(os.getenv("HEARTBEAT_FILE", MONITOR_DIR / "sonic_ledger.json"))

# -----------------------------
# 🖼️ UI Image Assets
# -----------------------------
SPACE_WALL_IMAGE = IMAGE_DIR / "space_wall2.jpg"
BTC_LOGO_IMAGE = IMAGE_DIR / "btc_logo.png"
ETH_LOGO_IMAGE = IMAGE_DIR / "eth_logo.png"
SOL_LOGO_IMAGE = IMAGE_DIR / "sol_logo.png"
THEME_CONFIG_WALLPAPER = IMAGE_DIR / "wallpaper_theme_page"
R2VAULT_IMAGE = IMAGE_DIR / "r2d2_icon.jpg"
OBIVAULT_IMAGE = IMAGE_DIR / "obi_icon.jpg"
LANDOVAULT_IMAGE = IMAGE_DIR / "lando_icon.jpg"
VADERVAULT_IMAGE = IMAGE_DIR / "vader_icon.jpg"
YODAVAULT_IMAGE = IMAGE_DIR / "yoda_icon.jpg"
BOBAVAULT_IMAGE = IMAGE_DIR / "boba_icon.jpg"
LEIAVAULT_IMAGE = IMAGE_DIR / "leia_icon.jpg"
C3P0VAULT_IMAGE = IMAGE_DIR / "c3po_icon.jpg"

JABBAVAULT_IMAGE = IMAGE_DIR / "jabba_icon.jpg"
CHEWBACCAVAULT_IMAGE = IMAGE_DIR / "chewie_icon.jpg"
PALPATINEVAULT_IMAGE = IMAGE_DIR / "palpatine_icon.jpg"
LUKEVAULT_IMAGE = IMAGE_DIR / "luke_icon.jpg"



# -----------------------------
# 🧠 Blockchain & RPC
# -----------------------------
POLYGON_RPC_URL = "https://polygon-rpc.com"

POOL_ADDRESS = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
POOL_PROVIDER_ADDR = "0xa97684ead0e402DC232d5A977953DF7ECBaB3CDb"
DATA_PROVIDER_ADDR = "0x69C7C30F2D9A9355Ab0F2F05aF28805F131B18C9"
LIQUIDATION_DATA_ADDR = "0xABCDEFabcdefABCDEFabcdefABCDEFabcdefABCD"

# -----------------------------
# ☄️ Jupiter API
# -----------------------------
JUPITER_API_BASE = os.getenv("JUPITER_API_BASE", "https://perps-api.jup.ag")

# -----------------------------
# 🧪 Contract ABIs
# -----------------------------
POOL_ABI = []

UI_POOL_DATA_PROVIDER_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "provider", "type": "address"},
            {"internalType": "address", "name": "user", "type": "address"}
        ],
        "name": "getUserReservesData",
        "outputs": [
            {
                "components": [
                    {"internalType": "address", "name": "reserve", "type": "address"},
                    {"internalType": "uint256", "name": "currentATokenBalance", "type": "uint256"},
                    {"internalType": "uint256", "name": "stableDebt", "type": "uint256"},
                    {"internalType": "uint256", "name": "variableDebt", "type": "uint256"}
                ],
                "internalType": "struct DataTypes.UserReserveData[]",
                "name": "",
                "type": "tuple[]"
            },
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

LIQ_DATA_PROVIDER_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "getUserPositionFullInfo",
        "outputs": [
            {"internalType": "uint256", "name": "totalCollateralBase", "type": "uint256"},
            {"internalType": "uint256", "name": "totalDebtBase", "type": "uint256"},
            {"internalType": "uint256", "name": "availableBorrowsBase", "type": "uint256"},
            {"internalType": "uint256", "name": "currentLiquidationThreshold", "type": "uint256"},
            {"internalType": "uint256", "name": "ltv", "type": "uint256"},
            {"internalType": "uint256", "name": "healthFactor", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# -----------------------------
# 💰 Asset Metadata (Optional)
# -----------------------------
ASSET_SYMBOLS = {
    # "0x...": "USDC",
}
ASSET_DECIMALS = {
    # "0x...": 6,
}
