from typing import Dict

from .oracle_data_service import OracleDataService


class AlertsTopicHandler:
    """Provide alerts context for GPT."""

    output_key = "alerts"
    system_message = "You summarize alert information."

    def __init__(self, data_locker):
        self.data_service = OracleDataService(data_locker)

    def get_context(self) -> Dict:
        alerts = self.data_service.fetch_alerts()
        return {self.output_key: alerts}
