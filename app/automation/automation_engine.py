import subprocess
import time
from datetime import date, datetime

from app.automation import config
from app.automation import keyboard_controller
from app.automation.window_manager import (
    bring_pharma_to_front,
    is_pharma_running,
    maximize_pharma_window,
    wait_for_window,
    wait_for_window_closed,
)
from app.core.models import ImportResult, ImportSummary
from app.tools.logger import get_import_logger, get_logger


class PurchaseAutomation:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def launch_pharma(self):
        self._log_action("launch_pharma", True, "Starting")

        if is_pharma_running(config.WINDOW_TITLE):
            brought_to_front = bring_pharma_to_front(config.WINDOW_TITLE)
            maximized = maximize_pharma_window(config.WINDOW_TITLE)
            success = brought_to_front and maximized
            self._log_action("launch_pharma", success, "Existing window path")
            return success

        try:
            subprocess.Popen([config.PHARMA_EXE_PATH])
            self._log_action("launch_pharma", True, f"Launched {config.PHARMA_EXE_PATH}")
        except Exception as error:
            self._log_action("launch_pharma", False, str(error))
            return False

        window_found = wait_for_window(
            config.WINDOW_TITLE,
            timeout=config.STARTUP_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        self._log_action("launch_pharma", window_found, "Launch path")
        return window_found

    def login(self):
        if not self.launch_pharma():
            self._log_action("login", False, "Unable to launch or focus Pharma")
            return False

        login_ready = wait_for_window(
            config.WINDOW_TITLE,
            timeout=config.LOGIN_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        if not login_ready:
            self._log_action("login", False, "Login window never appeared")
            return False

        steps = [
            keyboard_controller.write(config.USERNAME),
            keyboard_controller.press_enter(),
            keyboard_controller.write(config.PASSWORD),
            keyboard_controller.press_enter(),
        ]

        if not all(steps):
            self._log_action("login", False, "Login key sequence failed")
            return False

        loaded = wait_for_window(
            config.WINDOW_TITLE,
            timeout=config.LOGIN_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        self._log_action("login", loaded, "Main application load")
        return loaded

    def open_purchase_window(self):
        self._log_action("open_purchase_window", True, "Starting")

        brought_to_front = bring_pharma_to_front(config.WINDOW_TITLE)
        maximized = maximize_pharma_window(config.WINDOW_TITLE)
        if not (brought_to_front and maximized):
            self._log_action("open_purchase_window", False, "Main window not active")
            return False

        if not keyboard_controller.press_ctrl_p():
            self._log_action("open_purchase_window", False, "Ctrl+P failed")
            return False

        purchase_ready = wait_for_window(
            config.PURCHASE_BILL_WINDOW_TITLE,
            timeout=config.PURCHASE_WINDOW_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        if not purchase_ready:
            self._log_action("open_purchase_window", False, "Purchase Bill window not ready")
            return False

        cursor_ready = self.verify_date_field_ready()
        self._log_action("open_purchase_window", cursor_ready, "Date field ready")
        return cursor_ready

    def fill_header(self, invoice):
        self._log_action("fill_header", True, "Starting")

        invoice_date = format_invoice_date(invoice.invoice_date)
        today = format_today_date()

        steps = []

        self._log_action("Entering Date", True, invoice_date)
        steps.append(keyboard_controller.write(invoice_date))
        steps.append(keyboard_controller.press_enter())

        self._log_action("Confirming Credit", True)
        steps.append(keyboard_controller.press_enter())

        self._log_action("Confirming P Purc.", True)
        steps.append(keyboard_controller.press_enter())

        self._log_action("Skipping to Supplier", True)
        for _index in range(config.SUPPLIER_FIELD_TAB_COUNT):
            steps.append(keyboard_controller.press_enter())

        self._log_action("Selecting Supplier", True, invoice.supplier_name)
        steps.append(select_supplier(invoice.supplier_name))

        self._log_action("Entering Bill Number", True, invoice.invoice_number)
        steps.append(keyboard_controller.write(invoice.invoice_number))
        steps.append(keyboard_controller.press_enter())

        self._log_action("Entering Today's Date", True, today)
        steps.append(keyboard_controller.write(today))
        steps.append(keyboard_controller.press_enter())

        success = all(steps)
        self._log_action("Header Complete", success)
        return success

    def fill_items(self, invoice):
        total = len(invoice.items)
        successful_items = 0
        failed_items = []

        for index, item in enumerate(invoice.items, start=1):
            self._log_action(
                f"Medicine {index} / {total}",
                True,
                item.medicine_name,
            )

            if not self._fill_single_item(item):
                failed_items.append(item)
                self._log_action(
                    f"Medicine {index} / {total}",
                    False,
                    item.medicine_name,
                )
                continue

            successful_items += 1
            self._log_action(
                f"Medicine {index} / {total}",
                True,
                item.medicine_name,
            )

        return ImportResult(
            total=total,
            success=successful_items,
            failed=len(failed_items),
            failed_items=failed_items,
        )

    def save_purchase(self):
        self._log_action("save_purchase", True, "Starting")

        if not press_enters(config.SAVE_BUTTON_ENTER_COUNT):
            self._log_action("save_purchase", False, "Could not focus Save button")
            return False

        if not keyboard_controller.press_enter():
            self._log_action("save_purchase", False, "Save button submit failed")
            return False

        confirmation_ready = wait_for_window(
            config.SAVE_CONFIRMATION_WINDOW_TITLE,
            timeout=config.SAVE_CONFIRMATION_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        if not confirmation_ready:
            self._log_action("save_purchase", False, "Confirmation popup not found")
            return False

        if not keyboard_controller.press_enter():
            self._log_action("save_purchase", False, "Confirmation submit failed")
            return False

        closed = wait_for_window_closed(
            config.PURCHASE_BILL_WINDOW_TITLE,
            timeout=config.PURCHASE_CLOSE_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        self._log_action("save_purchase", closed, "Purchase Entry closed")
        return closed

    def run(self, invoice):
        start_time = datetime.now()
        self.import_logger = get_import_logger(start_time)
        self._log_action("run", True, "Starting import")

        import_result = ImportResult(
            total=len(invoice.items),
            success=0,
            failed=len(invoice.items),
            failed_items=list(invoice.items),
        )
        saved_successfully = False

        if not self.login():
            self._log_action("run", False, "Login failed")
            return self._build_summary(invoice, import_result, start_time, saved_successfully)

        if not self.open_purchase_window():
            self._log_action("run", False, "Purchase window failed")
            return self._build_summary(invoice, import_result, start_time, saved_successfully)

        if not self.fill_header(invoice):
            self._log_action("run", False, "Header entry failed")
            return self._build_summary(invoice, import_result, start_time, saved_successfully)

        import_result = self.fill_items(invoice)
        saved_successfully = self.save_purchase()
        return self._build_summary(invoice, import_result, start_time, saved_successfully)

    def verify_date_field_ready(self):
        self._log_action("verify_date_field_ready", True, "Assuming active field after window ready")
        return True

    def verify_next_item_row_ready(self):
        self._log_action("verify_next_item_row_ready", True, "Assuming cursor moved to next row")
        return True

    def _fill_single_item(self, item):
        self._log_action("Selecting Medicine", True, item.medicine_name)
        if not select_medicine(item.medicine_name):
            self._log_action("Selecting Medicine", False, item.medicine_name)
            return False

        steps = [
            enter_if_not_blank(item.batch_number),
            enter_if_not_blank(item.expiry),
            enter_if_not_blank(item.quantity),
            enter_free_quantity(item.free),
            enter_if_not_blank(item.purchase_rate),
            enter_if_not_blank(item.mrp),
            enter_if_not_blank(item.sale_rate),
            enter_if_not_blank(item.discount_percent),
            press_enters(config.REMAINING_ITEM_COLUMNS_ENTER_COUNT),
            self.verify_next_item_row_ready(),
        ]

        return all(steps)

    def _log_not_implemented(self, action):
        self.logger.info("Action: %s | Result: Failure | Not Implemented", action)
        print("Not Implemented")

    def _log_action(self, action, success, message=""):
        status = "Success" if success else "Failure"
        detail = f" | {message}" if message else ""
        self.logger.info("Action: %s | Result: %s%s", action, status, detail)
        if hasattr(self, "import_logger"):
            self.import_logger.info("Action: %s | Result: %s%s", action, status, detail)

    def _build_summary(self, invoice, import_result, start_time, saved_successfully):
        end_time = datetime.now()
        failed_medicine_names = [
            item.medicine_name for item in import_result.failed_items
        ]

        summary = ImportSummary(
            supplier=invoice.supplier_name,
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date,
            total_medicines=import_result.total,
            imported_successfully=import_result.success,
            failed=import_result.failed,
            failed_medicine_names=failed_medicine_names,
            start_time=start_time,
            end_time=end_time,
            duration=(end_time - start_time).total_seconds(),
            saved_successfully=saved_successfully,
        )
        self._log_import_summary(summary)
        return summary

    def _log_import_summary(self, summary):
        message = (
            f"Supplier={summary.supplier} | "
            f"Invoice Number={summary.invoice_number} | "
            f"Invoice Date={summary.invoice_date} | "
            f"Total Medicines={summary.total_medicines} | "
            f"Imported Successfully={summary.imported_successfully} | "
            f"Failed={summary.failed} | "
            f"Failed Medicine Names={summary.failed_medicine_names} | "
            f"Duration={summary.duration:.2f}s | "
            f"Saved Successfully={summary.saved_successfully}"
        )
        self.logger.info("Import Summary | %s", message)
        if hasattr(self, "import_logger"):
            self.import_logger.info("Import Summary | %s", message)


def select_supplier(name):
    logger = get_logger("select_supplier")
    supplier_name = str(name).strip()

    if not supplier_name:
        logger.info("Action: Selecting Supplier | Result: Failure | Supplier name is empty")
        return False

    for character in supplier_name:
        if not keyboard_controller.write(character):
            logger.info("Action: Selecting Supplier | Result: Failure | Character entry failed")
            return False
        time.sleep(config.SEARCH_DELAY)

    if config.SUPPLIER_DROPDOWN_PRESS_DOWN:
        if not keyboard_controller.press_down():
            logger.info("Action: Selecting Supplier | Result: Failure | Dropdown navigation failed")
            return False

    success = keyboard_controller.press_enter()
    status = "Success" if success else "Failure"
    logger.info("Action: Selecting Supplier | Result: %s | %s", status, supplier_name)
    return success


def select_medicine(name):
    logger = get_logger("select_medicine")
    medicine_name = str(name).strip()

    if not medicine_name:
        logger.info("Action: Selecting Medicine | Result: Failure | Medicine name is empty")
        return False

    typed_text = ""
    for character in medicine_name:
        typed_text += character
        if not keyboard_controller.write(character):
            logger.info("Action: Selecting Medicine | Result: Failure | %s", typed_text)
            return False
        time.sleep(config.SEARCH_DELAY)

    for retry_index in range(config.MEDICINE_SELECTION_RETRIES):
        if is_medicine_highlighted(medicine_name):
            success = keyboard_controller.press_enter()
            status = "Success" if success else "Failure"
            logger.info("Action: Selecting Medicine | Result: %s | %s", status, medicine_name)
            return success

        for _index in range(config.MEDICINE_MAX_DROPDOWN_STEPS):
            if config.MEDICINE_DROPDOWN_PRESS_DOWN and not keyboard_controller.press_down():
                logger.info("Action: Selecting Medicine | Result: Failure | Dropdown navigation failed")
                return False

            if is_medicine_highlighted(medicine_name):
                success = keyboard_controller.press_enter()
                status = "Success" if success else "Failure"
                logger.info("Action: Selecting Medicine | Result: %s | %s", status, medicine_name)
                return success

        logger.info(
            "Action: Selecting Medicine | Result: Failure | Retry %s/%s | %s",
            retry_index + 1,
            config.MEDICINE_SELECTION_RETRIES,
            medicine_name,
        )

    logger.info("Action: Selecting Medicine | Result: Failure | Not found: %s", medicine_name)
    return False


def is_medicine_highlighted(name):
    return True


def enter_if_not_blank(value):
    text = format_entry_value(value)
    if text and not keyboard_controller.write(text):
        return False
    return keyboard_controller.press_enter()


def enter_free_quantity(value):
    if numeric_greater_than_zero(value):
        return enter_if_not_blank(value)
    return keyboard_controller.press_enter()


def press_enters(count):
    for _index in range(count):
        if not keyboard_controller.press_enter():
            return False
    return True


def format_entry_value(value):
    if value is None:
        return ""
    return str(value).strip()


def numeric_greater_than_zero(value):
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def format_invoice_date(invoice_date):
    value = str(invoice_date).strip()
    if not value:
        return ""

    for date_format in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, date_format).strftime("%d/%m/%Y")
        except ValueError:
            continue

    return value.replace("-", "/")


def format_today_date():
    return date.today().strftime("%d-%m-%Y")
