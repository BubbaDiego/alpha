# cyclone/services/cyclone_wallet_service.py

from core.logging import log

class CycloneWalletService:
    def __init__(self, data_locker):
        self.dl = data_locker

    def add_wallet_interactive(self):
        try:
            name = input("Enter wallet name: ").strip()
            public_address = input("Enter public address: ").strip()
            private_address = input("Enter private address: ").strip()
            image_path = input("Enter image path (optional): ").strip()
            balance_str = input("Enter balance (optional): ").strip()

            try:
                balance = float(balance_str)
            except Exception:
                balance = 0.0

            wallet = {
                "name": name,
                "public_address": public_address,
                "private_address": private_address,
                "image_path": image_path,
                "balance": balance
            }

            self.dl.wallets.create_wallet(wallet)
            log.success(f"✅ Wallet '{name}' added successfully.", source="CycloneWalletService")
        except Exception as e:
            log.error(f"❌ Failed to add wallet: {e}", source="CycloneWalletService")

    def view_wallets(self):
        try:
            wallets = self.dl.wallets.get_wallets()
            if not wallets:
                print("⚠️ No wallets found.")
                return

            print("💼 Wallets")
            print(f"📦 Total: {len(wallets)}\n")
            for w in wallets:
                print(f"🧾 Name:     {w['name']}")
                print(f"🏦 Address:  {w['public_address']}")
                print(f"💰 Balance:  {w['balance']}")
                print(f"🖼️ Image:    {w['image_path']}")
                print("-" * 40)
        except Exception as e:
            log.error(f"❌ Error viewing wallets: {e}", source="CycloneWalletService")
