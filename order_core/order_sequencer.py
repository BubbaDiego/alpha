# order_core/order_sequencer.py

from typing import Optional


class OrderSequencer:
    """
    Composite order task manager.
    Groups atomic engine actions into higher-level flows.
    """

    def __init__(self, engine):
        self.engine = engine  # instance of OrderEngine

    async def run_full_open_position_flow(self, asset="SOL", kind="long", size="0.1", leverage="5x",
                                          order_type="market", collateral_asset="SOL"):
        """
        Full order configuration + confirm.
        Composite of: select asset → type → collateral → size → leverage → order type → confirm → wallet tx.
        """
        await self.engine.select_asset(asset)
        await self.engine.select_position_type(kind)
        await self.engine.select_collateral_asset(collateral_asset)
        await self.engine.set_position_size(size)
        await self.engine.set_leverage(leverage)
        await self.engine.select_order_type(order_type)

        await self.engine.confirm_order()
        await self.engine.confirm_wallet_transaction()

        return self.engine.get_order()

    async def run_tp_sl_flow(self, input_mint: str, output_mint: str,
                             in_amount: int, out_amount: int,
                             private_key: Optional[str] = None):
        """
        TP/SL setup and broadcast using Jupiter Trigger API.
        Wraps engine-level call into a safe sequence.
        """
        if not private_key:
            raise ValueError("Missing private key for TP/SL limit order")

        result = await self.engine.place_tp_sl_limit_order(
            input_mint=input_mint,
            output_mint=output_mint,
            in_amount=in_amount,
            out_amount=out_amount,
            private_key=private_key
        )
        return result

    async def run_modify_position_flow(self, kind: str, new_leverage: str):
        """
        Placeholder for a future composite flow that modifies leverage, collateral, etc.
        """
        await self.engine.select_position_type(kind)
        await self.engine.set_leverage(new_leverage)
        return self.engine.get_order()
