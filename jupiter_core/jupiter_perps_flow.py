import logging
from playwright.sync_api import Error
from data.models import Order  # Import the new Order model from models.py
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class JupiterPerpsFlow:
    def __init__(self, phantom_manager):
        """
        Initializes with an existing PhantomManager (SolflareManager) instance.
        :param phantom_manager: An instance of SolflareManager.
        """
        self.pm = phantom_manager
        self.page = phantom_manager.page
        self.order_definition = {}

    # PATCHED: only showing relevant method change

    async def select_position_type(self, position_type: str):
        logger.debug("Selecting position type: %s", position_type)
        if position_type.lower() == "long":
            try:
                await self.page.click("button:has-text('Long')", timeout=10000)
                logger.debug("✅ Long position selected.")
                self.order_definition["position_type"] = "long"
            except Error as e:
                logger.error("❌ Error selecting Long position: %s", e)
                raise
        elif position_type.lower() == "short":
            try:
                await self.page.click("button:has-text('Short')", timeout=10000)
                logger.debug("✅ Short position selected.")
                self.order_definition["position_type"] = "short"
            except Error as e:
                logger.error("❌ Error selecting Short position: %s", e)
                raise
        else:
            logger.error("❌ Invalid position type provided: %s", position_type)
            raise Exception("Invalid position type provided. Choose 'long' or 'short'.")

    def select_order_type(self, order_type: str):
        logger.debug("Selecting order type: %s", order_type)
        if order_type.lower() == "market":
            try:
                self.page.click("button:has-text('Market')", timeout=10000)
                logger.debug("✅ Market order type selected.")
                self.order_definition["order_type"] = "market"
            except Error as e:
                logger.error("❌ Error selecting Market order type: %s", e)
                raise
        elif order_type.lower() == "limit":
            try:
                self.page.click("button:has-text('Limit')", timeout=10000)
                logger.debug("✅ Limit order type selected.")
                self.order_definition["order_type"] = "limit"
            except Error as e:
                logger.error("❌ Error selecting Limit order type: %s", e)
                raise
        else:
            logger.error("❌ Invalid order type provided: %s", order_type)
            raise Exception("Invalid order type provided. Choose 'market' or 'limit'.")

    def select_payment_asset(self, asset_symbol: str):
        """
        Selects the payment/funding asset.
        :param asset_symbol: The asset symbol (e.g., SOL, USDT, USDC, WBTC, WETH).
        """
        logger.debug("Selecting payment asset: %s", asset_symbol)
        try:
            self.page.click("button.bg-v3-input-secondary-background", timeout=5000)
            logger.debug("Pulldown button clicked to reveal asset options.")
            self.page.click(f"li:has-text('{asset_symbol}')", timeout=5000)
            logger.debug("✅ Payment asset selected: %s", asset_symbol)
            self.order_definition["collateral_asset"] = asset_symbol.upper()
        except Error as e:
            logger.error("❌ Error selecting payment asset (%s): %s", asset_symbol, e)
            raise

    def set_position_size(self, size: str):
        logger.debug("Setting position size: %s", size)
        try:
            self.page.fill("input.position-size", size, timeout=5000)
            logger.debug("✅ Position size set to %s", size)
            self.order_definition["position_size"] = float(size)
        except Error as e:
            logger.error("❌ Error setting position size: %s", e)
            raise

    def set_leverage(self, leverage: str):
        logger.debug("Setting leverage: %s", leverage)
        try:
            desired = float(leverage.lower().replace("x", "").strip())
            min_val = 1.1
            max_val = 100.0
            slider_track = self.page.query_selector("div.rc-slider-track")
            if not slider_track:
                raise Exception("Slider track element not found")
            box = slider_track.bounding_box()
            ratio = (desired - min_val) / (max_val - min_val)
            target_x = box["x"] + ratio * box["width"]
            target_y = box["y"] + box["height"] / 2
            logger.debug("Calculated target coordinates for leverage: (%.2f, %.2f)", target_x, target_y)
            self.page.mouse.click(target_x, target_y)
            logger.debug("✅ Leverage set to %s", leverage)
            self.order_definition["leverage"] = desired
        except Error as e:
            logger.error("❌ Error setting leverage: %s", e)
            raise

    def switch_to_isolated_margin(self):
        """Switch the margin mode from Cross to Isolated."""
        logger.debug("Switching margin mode to Isolated")
        try:
            if self.page.is_visible("button:has-text('Cross')"):
                self.page.click("button:has-text('Cross')", timeout=5000)
            self.page.click("text=Isolated", timeout=5000)
            logger.debug("✅ Isolated margin selected")
            self.order_definition["margin_mode"] = "isolated"
        except Error as e:
            logger.error("❌ Error switching margin mode: %s", e)
            raise

    def capture_order_payload(self, url_keyword: str, timeout: int = 10000):
        logger.debug("Waiting for network request with keyword: %s", url_keyword)
        try:
            request = self.page.wait_for_event(
                "requestfinished",
                predicate=lambda req: url_keyword in req.url,
                timeout=timeout
            )
            try:
                payload = request.post_data_json()
            except Exception:
                payload = request.post_data()
            logger.debug("✅ Captured order payload: %s", payload)
            return payload
        except Error as e:
            logger.error("❌ Error capturing order payload: %s", e)
            raise

    def get_order(self):
        try:
            order = Order(
                asset=self.order_definition.get("asset", "UNKNOWN"),
                position_type=self.order_definition.get("position_type", ""),
                collateral_asset=self.order_definition.get("collateral_asset", ""),
                position_size=float(self.order_definition.get("position_size", 0)),
                leverage=float(self.order_definition.get("leverage", 0)),
                order_type=self.order_definition.get("order_type", "market"),
                entry_price=float(self.order_definition.get("entry_price", 0)),
                status="pending",
                fees=float(self.order_definition.get("fees", 0))
            )
            logger.debug("Created Order: %s", order)
            return order
        except Exception as e:
            logger.error("Error creating Order from order_definition: %s", e)
            raise

    def open_withdraw_modal(self):
        """
        Opens the secondary collateral management modal for withdrawals.
        Tries clicking a 'Manage Collateral' button; if not available, falls back to the first row’s collateral pencil.
        """
        modal_selector = "div.bg-v3-secondary-background"
        if self.page.is_visible(modal_selector):
            logger.debug("Secondary collateral modal already open.")
            return
        try:
            self.page.click("button:has-text('Manage Collateral')", timeout=5000)
            logger.debug("Clicked 'Manage Collateral' button to open modal.")
        except Error as e:
            logger.warning("Manage Collateral button not found; using fallback collateral pencil.")
            self.page.click("tr:first-of-type button.fill-current.text-v2-lily/50", timeout=5000)
        self.page.wait_for_selector(modal_selector, timeout=5000)
        logger.debug("Secondary collateral modal opened.")

    def withdraw_funds_modal(self, asset: str, position_type: str, withdraw_amount: str):
        """
        Withdraws funds using the secondary pop-up modal.
        Steps:
          1. Open the modal.
          2. Ensure the correct asset is selected.
          3. Fill in the withdrawal amount.
          4. Click the Confirm button.
          5. Capture the confirmation payload.
        """
        # 1. Open the modal.
        self.open_withdraw_modal()

        # 2. Ensure the correct asset is selected (if applicable).
        asset_selector = f"button.flex.items-center.space-x-3.rounded-lg:has-text('{asset.upper()}')"
        try:
            self.page.click(asset_selector, timeout=5000)
            logger.debug("Asset selected in modal: %s", asset.upper())
        except Error as e:
            logger.warning("Asset selection button not found; it might already be selected.")

        # 3. Fill in the withdrawal amount.
        withdraw_input_selector = "input[placeholder='0.00'][data-lpignore='true']"
        self.page.wait_for_selector(withdraw_input_selector, timeout=5000)
        self.page.fill(withdraw_input_selector, withdraw_amount, timeout=5000)
        logger.debug("Withdraw amount set to: %s", withdraw_amount)

        # 4. Click the Confirm button.
        confirm_button_selector = "button:has-text('Confirm')"
        self.page.click(confirm_button_selector, timeout=5000)
        logger.debug("Clicked Confirm in withdrawal modal.")

        # 5. Capture the confirmation payload.
        payload = self.capture_order_payload("withdraw", timeout=10000)
        logger.debug("Withdrawal confirmed, captured payload: %s", payload)
        return payload

    def withdraw_funds_row(self, asset: str, position_type: str, withdraw_amount: str):
        """
        Withdraws funds by clicking the collateral pencil in the position row.
        Steps:
          1. Click the collateral pencil in the correct row.
          2. Wait for the withdrawal modal to appear and fill in the withdrawal amount.
          3. Click the 'Withdraw' button.
          4. Capture the confirmation payload.
        """
        # 1. Click the collateral pencil.
        self.click_collateral_pencil(asset, position_type)

        # 2. Wait for the withdrawal modal's input field.
        withdraw_input_selector = "input[placeholder='0.00'][data-lpignore='true']"
        self.page.wait_for_selector(withdraw_input_selector, timeout=5000)

        # 3. Fill in the withdrawal amount.
        self.page.fill(withdraw_input_selector, withdraw_amount, timeout=5000)
        logger.debug("Withdraw amount set to: %s", withdraw_amount)

        # 4. Click the Withdraw button.
        withdraw_button_selector = "button:has-text('Withdraw')"
        self.page.click(withdraw_button_selector, timeout=5000)
        logger.debug("Clicked Withdraw button via row method, waiting for confirmation payload...")

        # 5. Capture the confirmation payload.
        payload = self.capture_order_payload("withdraw", timeout=10000)
        logger.debug("Withdrawal confirmed, captured payload: %s", payload)
        return payload

    def open_position(self, label: str = None):
        if label is None:
            position_type = self.order_definition.get("position_type", "Long").capitalize()
            asset = self.order_definition.get("asset", "SOL").upper()
            label = f"{position_type} {asset}"
        logger.debug("Opening position with label: %s", label)
        try:
            self.page.click(f"div.flex.items-center.justify-center.rounded-lg:has-text('{label}')", timeout=10000)
            logger.debug("Position open triggered with label: %s", label)
        except Error as e:
            logger.error("Error opening position with label %s: %s", label, e)
            raise
        print("Position opened.")

    def click_collateral_pencil(self, asset: str, position_type: str):
        position_type_cap = position_type.capitalize()
        row_selector = f"tr:has-text('{asset}'):has-text('{position_type_cap}')"
        pencil_selector = "button.fill-current.text-v2-primary"
        self.page.click(f"{row_selector} >> {pencil_selector}", timeout=5000)
        logger.debug(f"Clicked the pencil in {asset} {position_type} row.")
