import asyncio
import os
from cyclone_engine import Cyclone
from data.data_locker import DataLocker
# Import HedgeManager from the actual implementation location
from positions.hedge_manager import HedgeManager
from core.logging import log
from cyclone.cyclone_position_service import CyclonePositionService
from cyclone.cyclone_portfolio_service import CyclonePortfolioService
from cyclone.cyclone_alert_service import CycloneAlertService
from cyclone.cyclone_hedge_service import CycloneHedgeService

class CycloneConsoleService:
    def __init__(self, cyclone_instance):
        self.cyclone = cyclone_instance
        self.position_service = CyclonePositionService(cyclone_instance.data_locker)
        self.portfolio_service = CyclonePortfolioService(cyclone_instance.data_locker)
        self.alert_service = CycloneAlertService(cyclone_instance.data_locker)
        self.hedge_service = CycloneHedgeService(cyclone_instance.data_locker)

    def run(self):
        while True:
            print("\n=== Cyclone Interactive Console ===")
            print("1) 🌀 Run Full Cycle")
            print("2) 🗑️ Delete All Data")
            print("3) 💰 Prices")
            print("4) 📊 Positions")
            print("5) 🔔 Alerts")
            print("6) 🛡 Hedge")
            print("7) 🧹 Clear IDs")
            print("8) 💼 Wallets")
            print("9) 📝 Generate Cycle Report")
            print("10) ❌ Exit")
            choice = input("Enter your choice (1-10): ").strip()

            if choice == "1":
                print("Running full cycle (all steps)...")
                asyncio.run(self.cyclone.run_cycle())
                print("Full cycle completed.")
            elif choice == "2":
                self.cyclone.run_delete_all_data()
            elif choice == "3":
                self.run_prices_menu()
            elif choice == "4":
                self.run_positions_menu()
            elif choice == "5":
                self.run_alerts_menu()
            elif choice == "6":
                self.run_hedges_menu()
            elif choice == "7":
                print("Clearing stale IDs...")
                asyncio.run(self.cyclone.run_cleanse_ids())
            elif choice == "8":
                self.run_wallets_menu()
            elif choice == "9":
                print("Generating cycle report...")
                try:
                    #from cyclone_report_generator import generate_cycle_report
                    generate_cycle_report()
                    self.cyclone.u_logger.log_cyclone(
                        operation_type="Cycle Report Generated",
                        primary_text="Cycle report generated successfully",
                        source="Cyclone",
                        file="cyclone_engine.py"
                    )
                    print("Cycle report generated.")
                except Exception as e:
                    self.cyclone.logger.error(f"Cycle report generation failed: {e}", exc_info=True)
                    print(f"Cycle report generation failed: {e}")
            elif choice == "10":
                print("Exiting console mode.")
                break
            else:
                print("Invalid choice, please try again.")

    def run_console(self):
        while True:
            print("\n=== Cyclone Interactive Console ===")
            print("1) 🌀 Run Full Cycle")
            print("2) 🗑️ Delete All Data")
            print("3) 💰 Prices")
            print("4) 📊 Positions")
            print("5) 🔔 Alerts")
            print("6) 🛡 Hedge")
            print("7) 🧹 Clear IDs")
            print("8) 💼 Wallets")
            print("9) 📝 Generate Cycle Report")
            print("10) ❌ Exit")
            choice = input("Enter your choice (1-10): ").strip()

            if choice == "1":
                print("Running full cycle (all steps)...")
                asyncio.run(self.cyclone.run_cycle())
                print("Full cycle completed.")
            elif choice == "2":
                self.cyclone.run_delete_all_data()
            elif choice == "3":
                self.run_prices_menu()
            elif choice == "4":
                self.run_positions_menu()
            elif choice == "5":
                self.run_alerts_menu()
            elif choice == "6":
                self.cyclone.run_hedges_menu()
            elif choice == "7":
                print("Clearing stale IDs...")
                asyncio.run(self.cyclone.run_cleanse_ids())
            elif choice == "8":
                self.run_wallets_menu()
            elif choice == "9":
                print("Generating cycle report...")
                try:
                     #from cyclone_report_generator import generate_cycle_report
                    generate_cycle_report()  # External report generator
                    self.cyclone.u_logger.log_cyclone(
                        operation_type="Cycle Report Generated",
                        primary_text="Cycle report generated successfully",
                        source="Cyclone",
                        file="cyclone_engine.py"
                    )
                except Exception as e:
                    self.cyclone.logger.error(f"Cycle report generation failed: {e}", exc_info=True)
                    print(f"Cycle report generation failed: {e}")
            elif choice == "10":
                print("Exiting console mode.")
                break
            else:
                print("Invalid choice, please try again.")

    def run_prices_menu(self):
        while True:
            print("\n--- Prices Menu ---")
            print("1) 🚀 Market Update")
            print("2) 👁 View Prices")
            print("3) 🧹 Clear Prices")
            print("4) ↩️ Back to Main Menu")
            choice = input("Enter your choice (1-4): ").strip()
            if choice == "1":
                print("Running Market Update...")
                asyncio.run(self.cyclone.run_cycle(steps=["market_updates"]))
                print("Market Update completed.")
            elif choice == "2":
                print("Viewing Prices...")
                self.view_prices_backend()
            elif choice == "3":
                print("Clearing Prices...")
                self.cyclone.clear_prices_backend()
            elif choice == "4":
                break
            else:
                print("Invalid choice, please try again.")

    def run_positions_menu(self):
        while True:
            print("\n--- Positions Menu ---")
            print("1) 👁 View Positions")
            print("2) 🔄 Positions Updates")
            print("3) ✨ Enrich Positions")  # Renamed option for clarity
            print("4) 🧹 Clear Positions")
            print("5) ↩️ Back to Main Menu")
            choice = input("Enter your choice (1-5): ").strip()
            if choice == "1":
                print("Viewing Positions...")
                self.view_positions_backend()
            elif choice == "2":
                print("Running Position Updates...")
                asyncio.run(self.cyclone.run_position_updates())
                print("Position Updates completed.")
            elif choice == "3":
                print("Running Enrich Positions...")
                asyncio.run(self.cyclone.run_cycle(steps=["enrich_positions"]))
                print("Enrich Positions completed.")
            elif choice == "4":
                print("Clearing Positions...")
                #self.position_service.clear_positions_backend()
                asyncio.run(self.position_service.clear_positions_backend())

            elif choice == "5":
                break
            else:
                print("Invalid choice, please try again.")

        # In cyclone_console_helper.py (CycloneConsoleHelper class)

    def run_alerts_menu(self):
        while True:
            print("\n--- Alerts Menu ---")
            print("1) 👁 View Alerts")
            print("2) 💵 Create Market Alerts")
            print("3) 📊 Create Portfolio Alerts")
            print("4) 📌 Create Position Alerts")
            print("5) 🖥 Create Global Alerts")
            print("6) ✨ Enrich Alerts")
            print("7) 🔄 Update Evaluated Value")
            print("8) 🔍 Alert Evaluations")
            print("9) 🧹 Clear Alerts")
            print("10) ♻️ Refresh Alerts")
            print("11) ↩️ Back to Main Menu")
            choice = input("Enter your choice (1-11): ").strip()
            if choice == "1":
                print("Viewing Alerts...")
                self.view_alerts_backend()
            elif choice == "2":
                print("Creating Market Alerts...")
                asyncio.run(self.cyclone.run_cycle(steps=["create_market_alerts"]))
            elif choice == "3":
                print("Creating Portfolio Alerts...")
                asyncio.run(self.cyclone.run_create_portfolio_alerts())
            elif choice == "4":
                print("Creating Position Alerts...")
                asyncio.run(self.cyclone.run_cycle(steps=["create_position_alerts"]))
            elif choice == "5":
                print("Creating Global Alerts...")
                asyncio.run(self.cyclone.run_cycle(steps=["create_global_alerts"]))
            elif choice == "6":
                print("Running Enrich Alerts...")
                asyncio.run(self.cyclone.run_alert_enrichment())
                print("Enrich Alerts completed.")
            elif choice == "7":
                print("Updating Evaluated Values for Alerts...")
                asyncio.run(self.cyclone.run_cycle(steps=["update_evaluated_value"]))
            elif choice == "8":
                print("Running Alert Evaluations...")
                asyncio.run(self.cyclone.run_cycle(steps=["evaluate_alerts"]))
                print("Alert Evaluations completed.")
            elif choice == "9":
                print("Clearing Alerts...")
                self.cyclone.clear_alerts_backend()
            elif choice == "10":
                print("Refreshing Alerts...")
                asyncio.run(self.cyclone.run_alert_updates())
                print("Alerts refreshed.")
            elif choice == "11":
                break
            else:
                print("Invalid choice, please try again.")

    def run_hedges_menu(self):
        """
        Display a submenu for managing hedge data with these options:
          1) View Hedges – display current hedge data using the HedgeManager.
          2) Find Hedges – run the HedgeManager.find_hedges method to scan positions and assign new hedge IDs.
          3) Clear Hedges – clear all hedge associations from the database.
          4) Back to Main Menu.
        """


        while True:
            print("\n--- Hedges Menu ---")
            print("1) 👁 View Hedges")
            print("2) 🔍 Find Hedges")
            print("3) 🧹 Clear Hedges")
            print("4) ↩️ Back to Main Menu")
            choice = input("Enter your choice (1-4): ").strip()

            if choice == "1":
                # View hedges using current positions
                dl = get_locker()
                raw_positions = dl.read_positions()
                hedge_manager = HedgeManager(raw_positions)
                hedges = hedge_manager.get_hedges()
                if hedges:
                    print("\nCurrent Hedges:")
                    for hedge in hedges:
                        print(f"Hedge ID: {hedge.id}")
                        print(f"  Positions: {hedge.positions}")
                        print(f"  Total Long Size: {hedge.total_long_size}")
                        print(f"  Total Short Size: {hedge.total_short_size}")
                        print(f"  Long Heat Index: {hedge.long_heat_index}")
                        print(f"  Short Heat Index: {hedge.short_heat_index}")
                        print(f"  Total Heat Index: {hedge.total_heat_index}")
                        print(f"  Notes: {hedge.notes}")
                        print("-" * 40)
                else:
                    print("No hedges found.")
            elif choice == "2":
                # Find hedges: use the static method that scans positions, updates hedge_buddy_id, and returns hedge groups.
                dl = get_locker()
                groups = HedgeManager.find_hedges()
                if groups:
                    print(f"Found {len(groups)} hedge group(s) after scanning positions:")
                    for idx, group in enumerate(groups, start=1):
                        print(f"Group {idx}:")
                        for pos in group:
                            print(f"  Position ID: {pos.get('id')} (Type: {pos.get('position_type')})")
                        print("-" * 30)
                else:
                    print("No hedge groups found.")
            elif choice == "3":
                # Clear hedges: clear hedge associations from all positions.
                try:
                    HedgeManager.clear_hedge_data()
                    print("Hedge associations cleared.")
                except Exception as e:
                    print(f"Error clearing hedges: {e}")
            elif choice == "4":
                break
            else:
                print("Invalid choice, please try again.")

    def run_wallets_menu(self):
        while True:
            print("\n--- Wallets Menu ---")
            print("1) 👁 View Wallets")
            print("2) ➕ Add Wallet")
            print("3) 🧹 Clear Wallets")
            print("4) ↩️ Back to Main Menu")
            choice = input("Enter your choice (1-4): ").strip()
            if choice == "1":
                print("Viewing Wallets...")
                self.cyclone.view_wallets_backend()
            elif choice == "2":
                print("Adding Wallet...")
                self.cyclone.add_wallet_backend()
            elif choice == "3":
                print("Clearing Wallets...")
                self.cyclone.clear_wallets_backend()
            elif choice == "4":
                break
            else:
                print("Invalid choice, please try again.")

    def view_price_details(self, price: dict):
        print("━━━━━━━━━━━━ PRICE ━━━━━━━━━━━━")
        print(f"🆔 ID:           {price.get('id', '')}")
        print(f"💰 Asset:        {price.get('asset_type', '')}")
        print(f"💵 Current:      {price.get('current_price', '')}")
        print(f"↩️ Previous:     {price.get('previous_price', '')}")
        print(f"📅 Last Update:  {price.get('last_update_time', '')}")
        print(f"⏪ Prev Update:  {price.get('previous_update_time', '')}")
        print(f"📡 Source:       {price.get('source', '')}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    def view_position_details(self, pos: dict):
        print("━━━━━━━━━━ POSITION ━━━━━━━━━━")
        print(f"🆔 ID:           {pos.get('id', '')}")
        print(f"💰 Asset:        {pos.get('asset_type', '')}")
        print(f"📉 Type:         {pos.get('position_type', '')}")
        print(f"📈 Entry Price:  {pos.get('entry_price', '')}")
        print(f"🔄 Current:      {pos.get('current_price', '')}")
        print(f"💣 Liq. Price:   {pos.get('liquidation_price', '')}")
        print(f"🪙 Collateral:   {pos.get('collateral', '')}")
        print(f"📦 Size:         {pos.get('size', '')}")
        print(f"⚖ Leverage:      {pos.get('leverage', '')}x")
        print(f"💵 Value:        {pos.get('value', '')}")
        print(f"💰 PnL (net):    {pos.get('pnl_after_fees_usd', '')}")
        print(f"💼 Wallet:       {pos.get('wallet_name', '')}")
        print(f"🧠 Alert Ref:    {pos.get('alert_reference_id', '')}")
        print(f"🛡 Hedge ID:     {pos.get('hedge_buddy_id', '')}")
        print(f"📅 Updated:      {pos.get('last_updated', '')}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    def view_alert_details(self, alert: dict):
        print("━━━━━━━━━━━━ ALERT ━━━━━━━━━━━━")
        print(f"🆔 ID:               {alert.get('id', '')}")
        print(f"📅 Created:          {alert.get('created_at', '')}")
        print(f"📣 Type:             {alert.get('alert_type', '')}")
        print(f"🎯 Class:            {alert.get('alert_class', '')}")
        print(f"🔔 Notify:           {alert.get('notification_type', '')}")
        print(f"📊 Trigger:          {alert.get('trigger_value', '')}")
        print(f"🧮 Evaluated Value:  {alert.get('evaluated_value', '')}")
        print(f"🟡 Status:           {alert.get('status', '')} | Level: {alert.get('level', '')}")
        print(f"📈 Counter/Freq:     {alert.get('counter', 0)} / {alert.get('frequency', 1)}")
        print(f"💣 Liq Distance:     {alert.get('liquidation_distance', '')}")
        print(f"📉 Travel %:         {alert.get('travel_percent', '')}")
        print(f"💥 Liq Price:        {alert.get('liquidation_price', '')}")
        print(f"🧠 Position Ref:     {alert.get('position_reference_id', '')}")
        print(f"📝 Notes:            {alert.get('notes', '')}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    def paginate_items(self, items: list, display_fn: callable, title: str = "", page_size: int = 5):
        """
        🧾 Paginate and display a list of items using a display function.
        """
        if not items:
            print("⚠️ No records to display.")
            return

        index = 0
        total = len(items)
        total_pages = (total + page_size - 1) // page_size

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            current_page = (index // page_size) + 1
            print(f"\n📄 {title} — Showing {index + 1}-{min(index + page_size, total)} of {total}\n")

            for i in range(index, min(index + page_size, total)):
                display_fn(items[i])

            # Footer
            print(f"\n📘 Page {current_page} of {total_pages}")
            print("Commands: [N]ext | [P]rev | [Q]uit | [Enter]=Next/Quit")

            cmd = input("→ ").strip().lower()

            if cmd == "n":
                if index + page_size < total:
                    index += page_size
                else:
                    print("⚠️ Already on last page.")
            elif cmd == "p":
                if index - page_size >= 0:
                    index -= page_size
                else:
                    print("⚠️ Already on first page.")
            elif cmd == "q":
                break
            elif cmd == "":
                if index + page_size < total:
                    index += page_size
                else:
                    break  # treat Enter on last page as Quit
            else:
                print("⚠️ Invalid input.")

    def view_prices_backend(self):
        prices = self.cyclone.data_locker.prices.get_all_prices()
        self.paginate_items(prices, self.view_price_details, title="Latest Prices")

    def view_positions_backend(self):
        print("👁 [DEBUG] Viewer using DB path:", self.cyclone.data_locker.db.db_path)

        positions = self.cyclone.data_locker.positions.get_all_positions()

        if not positions:
            print("⚠️ No positions found in DB.")
        else:
            print(f"🧾 DEBUG: Pulled {len(positions)} positions from DB:")
            for pos in positions:
                print(f"  ➤ {pos.get('id')} — {pos.get('asset_type')} — {pos.get('wallet_name')}")

        self.paginate_items(positions, self.view_position_details, title="Open Positions")


    def view_alerts_backend(self):
        alerts = self.cyclone.data_locker.alerts.get_all_alerts()
        self.paginate_items(alerts, self.view_alert_details, title="Alert Definitions")


if __name__ == "__main__":
    from cyclone_engine import Cyclone

    from core.locker_factory import get_locker
    cyclone = Cyclone(poll_interval=60)
    helper = CycloneConsoleService(cyclone)
    helper.run()
