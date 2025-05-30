from typing import Dict

from .oracle_data_service import OracleDataService


class PricesTopicHandler:
    """Provide market prices context for GPT."""

    output_key = "prices"
    system_message = "You summarize price information."

    def __init__(self, data_locker):
        self.data_service = OracleDataService(data_locker)

    def get_context(self) -> Dict:
        prices = self.data_service.fetch_prices()
        return {self.output_key: prices}
