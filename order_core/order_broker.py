# order_core/order_broker.py

from typing import Dict


class OrderBroker:
    """
    Abstract base for broker implementations (Jupiter, API, future CEX).
    """
    def prepare_order(self, order_definition: Dict) -> Dict:
        raise NotImplementedError

    def enrich_order(self, payload: Dict) -> Dict:
        raise NotImplementedError

    def validate_payload(self, payload: Dict) -> bool:
        raise NotImplementedError


class JupiterBroker(OrderBroker):
    """
    Broker for Jupiter DEX. Currently non-networking — placeholder for validation only.
    """

    def prepare_order(self, order_definition: Dict) -> Dict:
        """
        Placeholder: Add fees, infer required mints, format numeric fields.
        """
        # Example of logic that might be here:
        payload = order_definition.copy()
        payload.setdefault("fees", 0.0)
        payload.setdefault("entry_price", 0.0)
        return payload

    def enrich_order(self, payload: Dict) -> Dict:
        """
        Could eventually fetch quote, slippage, or enrich from API.
        """
        return payload

    def validate_payload(self, payload: Dict) -> bool:
        """
        Run simple rules to ensure it's executable.
        """
        required_fields = ["asset", "position_type", "collateral_asset", "leverage", "position_size", "order_type"]
        return all(field in payload for field in required_fields)
