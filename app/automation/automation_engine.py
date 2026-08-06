from app.tools.logger import get_logger


class PurchaseAutomation:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def launch_pharma(self):
        self._log_not_implemented("launch_pharma")

    def login(self):
        self._log_not_implemented("login")

    def open_purchase_window(self):
        self._log_not_implemented("open_purchase_window")

    def fill_header(self):
        self._log_not_implemented("fill_header")

    def fill_items(self):
        self._log_not_implemented("fill_items")

    def save_purchase(self):
        self._log_not_implemented("save_purchase")

    def run(self):
        self._log_not_implemented("run")

    def _log_not_implemented(self, action):
        self.logger.info("Action: %s | Result: Failure | Not Implemented", action)
        print("Not Implemented")
