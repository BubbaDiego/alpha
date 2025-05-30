class BaseMonitor:
    def __init__(self, name: str, ledger_filename: str = None, timer_config_path: str = None):
        self.name = name
        self.ledger_filename = ledger_filename
        self.timer_config_path = timer_config_path

    def run_cycle(self):
        from core.logging import log
        from data.data_locker import DataLocker
        from core.core_imports import DB_PATH

        log.banner(f"🚀 Running {self.name}")
        result = {}
        status = "Success"
        try:
            result = self._do_work()

            if isinstance(result, dict):
                if "status" in result:
                    status = "Success" if str(result.get("status")).lower() == "success" else "Error"
                elif "success" in result:
                    status = "Success" if result.get("success") else "Error"
                elif "errors" in result:
                    status = "Success" if result.get("errors", 0) == 0 else "Error"
            

            # 🧾 Log to DB-backed ledger
            locker = DataLocker(DB_PATH)
            locker.ledger.insert_ledger_entry(
                monitor_name=self.name,
                status=status,
                metadata=result
            )

            log.success(f"{self.name} completed successfully.", source=self.name)

        except Exception as e:
            log.error(f"{self.name} failed: {e}", source=self.name)

            # 🧾 Still write failure to DB ledger
            locker = DataLocker(DB_PATH)
            locker.ledger.insert_ledger_entry(
                monitor_name=self.name,
                status="Error",
                metadata={"error": str(e)}
            )

    def _do_work(self):
        raise NotImplementedError("Monitors must implement `_do_work()`")
