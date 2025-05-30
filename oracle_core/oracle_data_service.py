class OracleDataService:
    """Provide data for the GPT Oracle context."""

    def __init__(self, data_locker):
        self.dl = data_locker

    def fetch_portfolio(self):
        return self.dl.portfolio.get_latest_snapshot()

    def fetch_alerts(self):
        return self.dl.alerts.get_all_alerts()[:20]

    def fetch_prices(self):
        return self.dl.prices.get_all_prices()[:20]

    def fetch_positions(self):
        """Return recent positions for context."""
        return self.dl.positions.get_all_positions()[:20]

    def fetch_death_log(self):
        return self.dl.get_death_log_entries()

    def fetch_system_alerts(self):
        return self.dl.get_system_alerts()

    def fetch_system(self):
        return {
            "last_update_times": self.dl.get_last_update_times(),
            "death_log": self.fetch_death_log(),
            "system_alerts": self.fetch_system_alerts(),
        }

    def get_topic_data(self, topic: str):
        if topic == "portfolio":
            return self.fetch_portfolio()
        if topic == "alerts":
            return self.fetch_alerts()
        if topic == "prices":
            return self.fetch_prices()
        if topic == "positions":
            return self.fetch_positions()
        if topic == "system":
            return self.fetch_system()
        raise ValueError(f"Unsupported topic: {topic}")
