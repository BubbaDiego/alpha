from typing import Dict

from calc_core.calc_services import CalcServices
from .oracle_data_service import OracleDataService


class PositionsTopicHandler:
    """Provide positions context for GPT.

    ``get_context`` fetches recent positions and calculates aggregate metrics
    via :class:`CalcServices`. The resulting average heat index is returned
    alongside the raw positions list.
    """

    output_key = "positions"
    system_message = "You summarize position information."

    def __init__(self, data_locker):
        self.data_service = OracleDataService(data_locker)

    def get_context(self) -> Dict:
        positions = self.data_service.fetch_positions()
        totals = CalcServices().calculate_totals(positions)
        return {
            self.output_key: positions,
            "avg_heat_index": totals.get("avg_heat_index", 0.0),
        }
