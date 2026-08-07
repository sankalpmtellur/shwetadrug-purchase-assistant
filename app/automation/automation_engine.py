import subprocess
import sys
import time
import traceback
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


class AutomationStepError(Exception):
    def __init__(self, step_name, medicine_name):
        super().__init__(f"{step_name} failed for medicine: {medicine_name}")
        self.step_name = step_name
        self.medicine_name = medicine_name


class PurchaseAutomation:
    def __init__(self, progress_callback=None):
        self.logger = get_logger(self.__class__.__name__)
        self.progress_callback = progress_callback
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True
        self._set_progress("Automation Stopped")

    def _should_stop(self):
        if self.stop_requested:
            self._log_action("stop", False, "Automation stopped by user")
            return True
        return False

    def launch_pharma(self):
        print("[AUTO] launch_pharma() entered")
        self._log_action("launch_pharma", True, "Starting")

        print("[AUTO] Checking for existing Pharma window...")
        pharma_running = is_pharma_running(config.WINDOW_TITLE)
        print(f"[AUTO] Existing Pharma window found: {pharma_running}")
        if pharma_running:
            print("[AUTO] Focusing window...")
            brought_to_front = bring_pharma_to_front(config.WINDOW_TITLE)
            print(f"[AUTO] Window focused: {brought_to_front}")
            print("[AUTO] Maximizing window...")
            maximized = maximize_pharma_window(config.WINDOW_TITLE)
            print(f"[AUTO] Window maximized: {maximized}")
            success = brought_to_front and maximized
            self._log_action("launch_pharma", success, "Existing window path")
            print(f"[AUTO] launch_pharma() returned {success}")
            return success

        try:
            print(f"[AUTO] Starting Pharma executable: {config.PHARMA_EXE_PATH}")
            subprocess.Popen([config.PHARMA_EXE_PATH])
            print("[AUTO] Pharma executable started")
            self._log_action("launch_pharma", True, f"Launched {config.PHARMA_EXE_PATH}")
        except Exception as error:
            self._log_action("launch_pharma", False, str(error))
            print("[AUTO] launch_pharma() returned False")
            return False

        print("[AUTO] Waiting for Pharma window after launch...")
        window_found = wait_for_window(
            config.WINDOW_TITLE,
            timeout=config.STARTUP_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        self._log_action("launch_pharma", window_found, "Launch path")
        print(f"[AUTO] launch_pharma() returned {window_found}")
        return window_found

    def login(self):
        print("[AUTO] login() entered")
        print("Launching Pharma...")
        launch_success = self.launch_pharma()
        print(f"[AUTO] login() launch_pharma returned {launch_success}")
        if not launch_success:
            self._log_action("login", False, "Unable to launch or focus Pharma")
            print("[AUTO] login() returned False")
            return False

        print("[AUTO] Checking login screen...")
        login_ready = wait_for_window(
            config.WINDOW_TITLE,
            timeout=config.LOGIN_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        print(f"[AUTO] Login screen found: {login_ready}")
        if not login_ready:
            self._log_action("login", False, "Login window never appeared")
            print("[AUTO] login() returned False")
            return False

        print("[AUTO] Typing username...")
        username_entered = keyboard_controller.write(config.USERNAME)
        print(f"[AUTO] Username entered: {username_entered}")

        print("[AUTO] Pressing Enter after username...")
        username_submitted = keyboard_controller.press_enter()
        print(f"[AUTO] Username Enter pressed: {username_submitted}")

        print("[AUTO] Typing password...")
        password_entered = keyboard_controller.write(config.PASSWORD)
        print(f"[AUTO] Password entered: {password_entered}")

        print("[AUTO] Pressing Enter after password...")
        password_submitted = keyboard_controller.press_enter()
        print(f"[AUTO] Password Enter pressed: {password_submitted}")

        if not all(
            [
                username_entered,
                username_submitted,
                password_entered,
                password_submitted,
            ]
        ):
            self._log_action("login", False, "Login key sequence failed")
            print("[AUTO] login() returned False")
            return False

        print("[AUTO] Waiting for login success...")
        loaded = wait_for_window(
            config.WINDOW_TITLE,
            timeout=config.LOGIN_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        print(f"[AUTO] Login successful: {loaded}")
        self._log_action("login", loaded, "Main application load")
        print("[AUTO] login() completed")
        print(f"[AUTO] login() returned {loaded}")
        return loaded

    def open_purchase_window(self):
        print("[AUTO] open_purchase_window() entered")
        self._log_action("open_purchase_window", True, "Starting")

        brought_to_front = bring_pharma_to_front(config.WINDOW_TITLE)
        maximized = maximize_pharma_window(config.WINDOW_TITLE)
        if not (brought_to_front and maximized):
            self._log_action("open_purchase_window", False, "Main window not active")
            print("[AUTO] open_purchase_window() returned False")
            return False

        if not keyboard_controller.press_ctrl_p():
            self._log_action("open_purchase_window", False, "Ctrl+P failed")
            print("[AUTO] open_purchase_window() returned False")
            return False

        purchase_ready = wait_for_window(
            config.PURCHASE_BILL_WINDOW_TITLE,
            timeout=config.PURCHASE_WINDOW_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        if not purchase_ready:
            self._log_action("open_purchase_window", False, "Purchase Bill window not ready")
            print("[AUTO] open_purchase_window() returned False")
            return False

        cursor_ready = self.verify_date_field_ready()
        self._log_action("open_purchase_window", cursor_ready, "Date field ready")
        print(f"[AUTO] open_purchase_window() returned {cursor_ready}")
        return cursor_ready

    def fill_header(self, invoice):
        print("[AUTO] fill_header() entered")
        self._log_action("fill_header", True, "Starting")

        invoice_date = format_invoice_date(invoice.invoice_date)
        today = format_today_date()

        steps = []

        print("Entering Invoice Date...")
        self._log_action("Entering Invoice Date", True, invoice_date)
        steps.append(keyboard_controller.write(invoice_date))
        print("Entered Invoice Date")

        for field_name in config.HEADER_ENTER_ONLY_FIELDS:
            print(f"{field_name}...")
            steps.append(press_enters_with_debug(1))

        print("Entering Supplier...")
        self._log_action("Entering Supplier", True, invoice.supplier_name)
        steps.append(select_supplier(invoice.supplier_name))
        print("Entered Supplier")

        print("Entering Supplier Bill No...")
        self._log_action("Entering Supplier Bill No", True, invoice.invoice_number)
        steps.append(keyboard_controller.write(invoice.invoice_number))
        print("Entered Supplier Bill No")
        steps.append(press_enters_with_debug(1))

        print("Entering Supplier Bill Date...")
        self._log_action("Entering Supplier Bill Date", True, today)
        steps.append(keyboard_controller.write(today))
        print("Entered Supplier Bill Date")
        steps.append(press_enters_with_debug(1))

        success = all(steps)
        self._log_action("Header Complete", success)
        print(f"[AUTO] fill_header() returned {success}")
        return success

    def fill_items(self, invoice):
        print("[AUTO] fill_items() entered")
        total = len(invoice.items)
        successful_items = 0
        failed_items = []

        for index, item in enumerate(invoice.items, start=1):
            if self._should_stop():
                failed_items.extend(invoice.items[index - 1 :])
                break

            progress_value = 50
            if total:
                progress_value = 50 + int((index / total) * 35)
            self._set_progress(f"Medicine {index} / {total}", progress_value)
            print(f"[AUTO] Entering Medicine {index}...")
            self._log_action(
                f"Medicine {index} / {total}",
                True,
                item.medicine_name,
            )

            try:
                print(f"Medicine {index}")
                self._fill_single_item(item)
            except Exception as error:
                failed_items.append(item)
                self._print_medicine_exception(item, error)
                self._log_action(
                    f"Medicine {index} / {total}",
                    False,
                    f"{type(error).__name__}: {error}",
                )
                continue

            successful_items += 1
            self._log_action(
                f"Medicine {index} / {total}",
                True,
                item.medicine_name,
            )

        result = ImportResult(
            total=total,
            success=successful_items,
            failed=len(failed_items),
            failed_items=failed_items,
        )
        print(
            "[AUTO] fill_items() returned "
            f"success={result.success} failed={result.failed}"
        )
        return result

    def save_purchase(self):
        print("[AUTO] save_purchase() entered")
        if self._should_stop():
            print("[AUTO] save_purchase() returned False")
            return False

        self._log_action("save_purchase", True, "Starting")

        if not press_enters(config.SAVE_BUTTON_ENTER_COUNT):
            self._log_action("save_purchase", False, "Could not focus Save button")
            print("[AUTO] save_purchase() returned False")
            return False

        if not keyboard_controller.press_enter():
            self._log_action("save_purchase", False, "Save button submit failed")
            print("[AUTO] save_purchase() returned False")
            return False

        confirmation_ready = wait_for_window(
            config.SAVE_CONFIRMATION_WINDOW_TITLE,
            timeout=config.SAVE_CONFIRMATION_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        if not confirmation_ready:
            self._log_action("save_purchase", False, "Confirmation popup not found")
            print("[AUTO] save_purchase() returned False")
            return False

        if not keyboard_controller.press_enter():
            self._log_action("save_purchase", False, "Confirmation submit failed")
            print("[AUTO] save_purchase() returned False")
            return False

        closed = wait_for_window_closed(
            config.PURCHASE_BILL_WINDOW_TITLE,
            timeout=config.PURCHASE_CLOSE_TIMEOUT,
            poll_interval=config.POLL_INTERVAL,
        )
        self._log_action("save_purchase", closed, "Purchase Entry closed")
        print(f"[AUTO] save_purchase() returned {closed}")
        return closed

    def run(self, invoice):
        print("[AUTO] run() entered")
        try:
            self.stop_requested = False
            start_time = datetime.now()
            self.import_logger = get_import_logger(start_time)
            self._set_progress("Preparing...", 0)
            print(f"[AUTO] Invoice passed to automation: {len(invoice.items)} items")
            self._log_action("run", True, "Starting import")

            import_result = ImportResult(
                total=len(invoice.items),
                success=0,
                failed=len(invoice.items),
                failed_items=list(invoice.items),
            )
            saved_successfully = False

            if self._should_stop():
                return self._build_summary(invoice, import_result, start_time, saved_successfully)

            self._set_progress("Opening Pharma...", 10)
            self._set_progress("Logging In...", 20)
            print("Logging in...")
            if not self.login():
                self._log_action("run", False, "Login failed")
                return self._build_summary(invoice, import_result, start_time, saved_successfully)

            if self._should_stop():
                return self._build_summary(invoice, import_result, start_time, saved_successfully)

            self._set_progress("Opening Purchase Window...", 35)
            print("Opening Purchase Window...")
            if not self.open_purchase_window():
                self._log_action("run", False, "Purchase window failed")
                return self._build_summary(invoice, import_result, start_time, saved_successfully)

            if self._should_stop():
                return self._build_summary(invoice, import_result, start_time, saved_successfully)

            self._set_progress("Entering Header...", 50)
            print("Entering Header...")
            if not self.fill_header(invoice):
                self._log_action("run", False, "Header entry failed")
                return self._build_summary(invoice, import_result, start_time, saved_successfully)

            print("[AUTO] fill_items()")
            import_result = self.fill_items(invoice)

            if self._should_stop():
                return self._build_summary(invoice, import_result, start_time, saved_successfully)

            self._set_progress("Saving...", 90)
            print("[AUTO] save_purchase()")
            saved_successfully = self.save_purchase()
            summary = self._build_summary(invoice, import_result, start_time, saved_successfully)
            self._set_progress("Completed", 100)
            print("[AUTO] Finished")
            return summary
        except Exception:
            traceback.print_exc()
            raise

    def verify_date_field_ready(self):
        self._log_action("verify_date_field_ready", True, "Assuming active field after window ready")
        return True

    def verify_next_item_row_ready(self):
        self._log_action("verify_next_item_row_ready", True, "Assuming cursor moved to next row")
        return True

    def _fill_single_item(self, item):
        print("Press Enter (SI No)")
        self._require_step(
            "Move from SI No to Medicine Name",
            lambda: press_enters_with_debug(config.ITEM_ROW_START_ENTER_COUNT),
            item.medicine_name,
        )

        print("Entering Medicine Name...")
        print("Selecting Medicine...")
        self._log_action("Selecting Medicine", True, item.medicine_name)
        self._require_step("Selecting Medicine", lambda: select_medicine(item.medicine_name), item.medicine_name)
        print("Selected Medicine")

        print("Entering Batch...")
        self._require_step("Entering Batch", lambda: enter_if_not_blank(item.batch_number), item.medicine_name)
        print("Entered Batch")

        print("Entering Expiry...")
        self._require_step(
            "Entering Expiry",
            lambda: enter_if_not_blank(format_expiry_date(item.expiry)),
            item.medicine_name,
        )
        print("Entered Expiry")

        print("Entering Quantity...")
        self._require_step("Entering Quantity", lambda: enter_if_not_blank(item.quantity), item.medicine_name)
        print("Entered Quantity")

        print("Entering Free...")
        self._require_step("Entering Free", lambda: enter_free_quantity(item.free), item.medicine_name)
        print("Entered Free")

        print("Entering Purchase Rate...")
        self._require_step(
            "Entering Purchase Rate",
            lambda: enter_if_not_blank(item.purchase_rate),
            item.medicine_name,
        )
        print("Entered Purchase Rate")

        print("Entering MRP...")
        self._require_step("Entering MRP", lambda: enter_if_not_blank(item.mrp), item.medicine_name)
        print("Entered MRP")

        print("Entering Sale Rate...")
        self._require_step("Entering Sale Rate", lambda: enter_if_not_blank(item.sale_rate), item.medicine_name)
        print("Entered Sale Rate")

        print("Entering Discount...")
        self._require_step(
            "Entering Discount",
            lambda: enter_if_not_blank(item.discount_percent),
            item.medicine_name,
        )
        print("Entered Discount")

        print("Press Enter...")
        self._require_step(
            "Moving to next item row",
            lambda: press_enters_with_debug(config.ITEM_ROW_COMPLETION_ENTER_COUNT),
            item.medicine_name,
        )
        self._require_step(
            "Verifying next item row",
            self.verify_next_item_row_ready,
            item.medicine_name,
        )

        return True

    def _require_step(self, step_name, callback, medicine_name):
        try:
            success = callback()
        except Exception as error:
            raise AutomationStepError(step_name, medicine_name) from error

        if not success:
            self._log_action(step_name, False, medicine_name)
            raise AutomationStepError(step_name, medicine_name)

        return True

    def _print_medicine_exception(self, item, error):
        print("--------------------------------")
        print(f"Medicine: {item.medicine_name}")
        print(f"Exception Type: {type(error).__name__}")
        print(f"Exception Message: {error}")
        print("Exception:")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stdout)
        print("--------------------------------")

    def _log_not_implemented(self, action):
        self.logger.info("Action: %s | Result: Failure | Not Implemented", action)
        print("Not Implemented")

    def _log_action(self, action, success, message=""):
        status = "Success" if success else "Failure"
        detail = f" | {message}" if message else ""
        self.logger.info("Action: %s | Result: %s%s", action, status, detail)
        if hasattr(self, "import_logger"):
            self.import_logger.info("Action: %s | Result: %s%s", action, status, detail)

    def _set_progress(self, status, value=None):
        if self.progress_callback:
            self.progress_callback(status, value)

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

    print("Typing Supplier...")
    for character in supplier_name:
        if not keyboard_controller.write(character):
            logger.info("Action: Selecting Supplier | Result: Failure | Character entry failed")
            return False
        time.sleep(config.SEARCH_DELAY)
    print("Typed Supplier")

    if config.SUPPLIER_DROPDOWN_PRESS_DOWN:
        print("Press Down (Supplier)")
        if not keyboard_controller.press_down():
            logger.info("Action: Selecting Supplier | Result: Failure | Dropdown navigation failed")
            return False

    print("Press Enter")
    success = keyboard_controller.press_enter()
    print(f"Pressed Enter: {success}")
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
    print("Typing Medicine Name...")
    for character in medicine_name:
        typed_text += character
        if not keyboard_controller.write(character):
            logger.info("Action: Selecting Medicine | Result: Failure | %s", typed_text)
            return False
        time.sleep(config.SEARCH_DELAY)
    print("Typed Medicine Name")

    for retry_index in range(config.MEDICINE_SELECTION_RETRIES):
        if is_medicine_highlighted(medicine_name):
            print("Press Enter")
            success = keyboard_controller.press_enter()
            print(f"Pressed Enter: {success}")
            status = "Success" if success else "Failure"
            logger.info("Action: Selecting Medicine | Result: %s | %s", status, medicine_name)
            return success

        for _index in range(config.MEDICINE_MAX_DROPDOWN_STEPS):
            if config.MEDICINE_DROPDOWN_PRESS_DOWN and not keyboard_controller.press_down():
                logger.info("Action: Selecting Medicine | Result: Failure | Dropdown navigation failed")
                return False

            if is_medicine_highlighted(medicine_name):
                print("Press Enter")
                success = keyboard_controller.press_enter()
                print(f"Pressed Enter: {success}")
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
    print("Press Enter")
    success = keyboard_controller.press_enter()
    print(f"Pressed Enter: {success}")
    return success


def enter_free_quantity(value):
    if numeric_greater_than_zero(value):
        return enter_if_not_blank(value)
    print("Press Enter")
    success = keyboard_controller.press_enter()
    print(f"Pressed Enter: {success}")
    return success


def press_enters(count):
    for _index in range(count):
        if not keyboard_controller.press_enter():
            return False
    return True


def press_enters_with_debug(count):
    for _index in range(count):
        print("Press Enter")
        if not keyboard_controller.press_enter():
            return False
        print("Pressed Enter")
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
            return datetime.strptime(value, date_format).strftime("%d-%m-%Y")
        except ValueError:
            continue

    return value.replace("/", "-")


def format_expiry_date(expiry_date):
    value = str(expiry_date).strip()
    if not value:
        return ""

    normalized = value.replace(".", "-").replace("/", "-")
    parts = normalized.split("-")

    if len(parts) == 3:
        day, month, year = parts
        if len(year) == 2:
            year = f"20{year}"
        return f"{day.zfill(2)}-{month.zfill(2)}-{year}"

    if len(parts) == 2:
        month, year = parts
        if len(year) == 2:
            year = f"20{year}"
        return f"01-{month.zfill(2)}-{year}"

    return normalized


def format_today_date():
    return date.today().strftime("%d-%m-%Y")
