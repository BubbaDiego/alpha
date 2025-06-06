import json
import sys
import os

# Correct absolute path based on your setup
wallet_json_path = r'C:\alpha\wallets\star_wars\star_wars_wallets.json'

# Add the project root to the Python path
sys.path.append(r'C:\alpha')

from wallets.wallet_core import WalletCore
from wallets.wallet import Wallet

with open(wallet_json_path, 'r') as file:
    data = json.load(file)

wallet_core = WalletCore()
1
for wallet_info in data['wallets']:
    wallet = Wallet(
        name=wallet_info['name'],
        public_address=wallet_info['public'],
        private_address=wallet_info.get('private_key'),
        image_path=wallet_info['image'],
        tags=["star_wars", "imported"],
        is_active=True,
        type="personal"
    )

    wallet_core.service.create_wallet(wallet)
    print(f"Inserted wallet: {wallet.name}")

print("All wallets have been inserted into the database.")
