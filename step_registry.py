from typing import Callable, Dict
from jupiter_auto_engine import JupiterAutoEngine


def build_step_registry(engine: JupiterAutoEngine) -> Dict[str, Callable[[], None]]:
    return {
        "connect_wallet": engine.step_connect_wallet,
        "unlock_wallet": engine.step_unlock_wallet,
        "set_position_type": lambda: engine.step_set_position_type("long"),
        "set_payment_asset": lambda: engine.step_set_payment_asset("USDC"),
        "set_leverage": lambda: engine.step_set_leverage("7x"),
        "set_position_size": lambda: engine.step_set_position_size("1.0"),
        "approve_transaction": engine.step_approve_transaction,
        "capture_order_payload": lambda: engine.step_capture_order_payload("order-submit"),
    }
