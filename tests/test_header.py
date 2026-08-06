from pathlib import Path
import sys
from unittest.mock import Mock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.automation_engine import (
    PurchaseAutomation,
    format_invoice_date,
    format_today_date,
    select_supplier,
)
from app.core.models import Invoice


def test_format_invoice_date():
    assert format_invoice_date("2026-08-06") == "06/08/2026"
    assert format_invoice_date("06-08-2026") == "06/08/2026"
    assert format_invoice_date("06/08/2026") == "06/08/2026"


def test_format_today_date():
    fake_date = Mock()
    fake_date.today.return_value.strftime.return_value = "06-08-2026"

    with patch("app.automation.automation_engine.date", fake_date):
        assert format_today_date() == "06-08-2026"


def test_open_purchase_window_success():
    automation = PurchaseAutomation()

    with patch("app.automation.automation_engine.bring_pharma_to_front", return_value=True), \
        patch("app.automation.automation_engine.maximize_pharma_window", return_value=True), \
        patch("app.automation.automation_engine.keyboard_controller.press_ctrl_p", return_value=True), \
        patch("app.automation.automation_engine.wait_for_window", return_value=True), \
        patch.object(automation, "verify_date_field_ready", return_value=True):
        assert automation.open_purchase_window() is True


def test_select_supplier_types_progressively():
    with patch("app.automation.automation_engine.keyboard_controller.write", return_value=True) as write, \
        patch("app.automation.automation_engine.keyboard_controller.press_enter", return_value=True) as enter, \
        patch("app.automation.automation_engine.time.sleep", return_value=None):
        assert select_supplier("ABC") is True
        assert [call.args[0] for call in write.call_args_list] == ["A", "B", "C"]
        enter.assert_called_once()


def test_fill_header_sequence_and_supplier_helper():
    automation = PurchaseAutomation()
    invoice = Invoice(
        supplier_name="ABC Pharma",
        invoice_number="INV-1001",
        invoice_date="2026-08-06",
    )

    with patch("app.automation.automation_engine.keyboard_controller.write", return_value=True) as write, \
        patch("app.automation.automation_engine.keyboard_controller.press_enter", return_value=True) as enter, \
        patch("app.automation.automation_engine.select_supplier", return_value=True) as supplier, \
        patch("app.automation.automation_engine.format_today_date", return_value="06-08-2026"), \
        patch("app.automation.config.SUPPLIER_FIELD_TAB_COUNT", 4):
        assert automation.fill_header(invoice) is True

        assert write.call_args_list[0].args[0] == "06/08/2026"
        assert write.call_args_list[1].args[0] == "INV-1001"
        assert write.call_args_list[2].args[0] == "06-08-2026"
        supplier.assert_called_once_with("ABC Pharma")
        assert enter.call_count == 6


if __name__ == "__main__":
    test_format_invoice_date()
    test_format_today_date()
    test_open_purchase_window_success()
    test_select_supplier_types_progressively()
    test_fill_header_sequence_and_supplier_helper()
