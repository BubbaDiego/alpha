# order_core/order_core.py

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from order_core.order_engine import OrderEngine
from order_core.order_sequencer import OrderSequencer
from order_core.order_broker import JupiterBroker
from order_core.agent_phantom import PhantomAgent
from order_core.agent_solflare import SolflareAgent
from order_core.order_model import OrderModel
from typing import Optional, Literal


WalletType = Literal["phantom", "solflare"]


class OrderCore:
    """
    Central orchestrator for all order tasks.
    Mirrors CycloneCore: configures broker, wallet agent, engine, and sequencer.
    """

    def __init__(self, data_locker, config_loader, wallet_type: WalletType = "phantom"):
        self.dl = data_locker
        self.config = config_loader()
        self.wallet_type = wallet_type

        self.agent = None
        self.broker = None
        self.engine = None
        self.sequencer = None

    async def launch(self, extension_path: str, headless: bool = False,
                     phantom_password: Optional[str] = None,
                     solflare_password: Optional[str] = None):
        """
        Boot sequence: load wallet, connect, build broker/engine/sequencer.
        """
        # Initialize wallet agent
        if self.wallet_type == "phantom":
            self.agent = PhantomAgent(extension_path=extension_path, headless=headless)
            await self.agent.launch_browser()
            if phantom_password:
                await self.agent.unlock(phantom_password)
        elif self.wallet_type == "solflare":
            self.agent = SolflareAgent(extension_path=extension_path, headless=headless)
            await self.agent.launch_browser()
            if solflare_password:
                await self.agent.unlock(solflare_password)
        else:
            raise ValueError(f"Unsupported wallet type: {self.wallet_type}")

        # Load broker
        self.broker = JupiterBroker()

        # Build engine and sequencer
        self.engine = OrderEngine(agent=self.agent, broker=self.broker)
        self.sequencer = OrderSequencer(engine=self.engine)

    async def sync_wallet(self, dapp_url: str):
        """
        Navigates to dApp and triggers connection via wallet modal.
        """
        await self.agent.connect_wallet(dapp_url)

    async def run_order_flow(self, **kwargs) -> OrderModel:
        """
        Runs full order flow and returns an OrderModel.
        kwargs: asset, kind, size, leverage, order_type, collateral_asset
        """
        return await self.sequencer.run_full_open_position_flow(**kwargs)

    async def run_tp_sl_flow(self, input_mint, output_mint, in_amount, out_amount, private_key) -> str:
        """
        Runs TP/SL trigger flow.
        """
        return await self.sequencer.run_tp_sl_flow(
            input_mint=input_mint,
            output_mint=output_mint,
            in_amount=in_amount,
            out_amount=out_amount,
            private_key=private_key
        )

    async def get_order_summary(self) -> Optional[OrderModel]:
        """
        Returns latest constructed order object from engine.
        """
        return self.engine.get_order()
