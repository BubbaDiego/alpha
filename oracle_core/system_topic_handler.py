from typing import Dict

from .oracle_data_service import OracleDataService


class SystemTopicHandler:
    """Provide system state context for GPT."""

    output_key = "system"
    system_message = "You report system status."

    def __init__(self, data_locker):
        self.data_service = OracleDataService(data_locker)

    def get_context(self) -> Dict:
        system = self.data_service.fetch_system()
        return {self.output_key: system}
