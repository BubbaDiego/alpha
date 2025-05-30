from typing import Dict

from .oracle_data_service import OracleDataService


class PortfolioTopicHandler:
    """Provide portfolio context for GPT."""

    output_key = "portfolio"
    system_message = "You are a portfolio analysis assistant."

    def __init__(self, data_locker):
        self.data_service = OracleDataService(data_locker)

    def get_context(self) -> Dict:
        snapshot = self.data_service.fetch_portfolio()
        return {self.output_key: snapshot}
