from datetime import datetime
from decimal import Decimal
from pathlib import Path
import sys
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.automation_engine import PurchaseAutomation
from app.core.models import ImportResult, ImportSummary, Invoice, InvoiceItem
from app.core.text_parser import parse_invoice_text


def make_invoice():
    item = InvoiceItem(
        medicine_name="Dolo 650",
        batch_number="B001",
        expiry="01.10.27",
        quantity=Decimal("10"),
        free=Decimal("0"),
        purchase_rate=Decimal("12.50"),
        mrp=Decimal("20.00"),
        sale_rate=Decimal("18.00"),
        discount_percent=Decimal("5"),
    )
    return Invoice("ABC Pharma", "INV-1001", "2026-08-06", items=[item])


def test_save_purchase_success_path():
    automation = PurchaseAutomation()

    with patch("app.automation.automation_engine.press_enters", return_value=True), \
        patch("app.automation.automation_engine.keyboard_controller.press_enter", return_value=True), \
        patch("app.automation.automation_engine.wait_for_window", return_value=True), \
        patch("app.automation.automation_engine.wait_for_window_closed", return_value=True):
        assert automation.save_purchase() is True


def test_save_purchase_failure_path():
    automation = PurchaseAutomation()

    with patch("app.automation.automation_engine.press_enters", return_value=False):
        assert automation.save_purchase() is False


def test_run_complete_success_workflow():
    invoice = make_invoice()
    automation = PurchaseAutomation()
    import_result = ImportResult(total=1, success=1, failed=0, failed_items=[])

    with patch.object(automation, "login", return_value=True), \
        patch.object(automation, "open_purchase_window", return_value=True), \
        patch.object(automation, "fill_header", return_value=True), \
        patch.object(automation, "fill_items", return_value=import_result), \
        patch.object(automation, "save_purchase", return_value=True), \
        patch("app.automation.automation_engine.get_import_logger"):
        summary = automation.run(invoice)

    assert isinstance(summary, ImportSummary)
    assert summary.supplier == "ABC Pharma"
    assert summary.invoice_number == "INV-1001"
    assert summary.total_medicines == 1
    assert summary.imported_successfully == 1
    assert summary.failed == 0
    assert summary.failed_medicine_names == []
    assert summary.saved_successfully is True


def test_run_failure_summary_when_login_fails():
    invoice = make_invoice()
    automation = PurchaseAutomation()

    with patch.object(automation, "login", return_value=False), \
        patch("app.automation.automation_engine.get_import_logger"):
        summary = automation.run(invoice)

    assert summary.total_medicines == 1
    assert summary.imported_successfully == 0
    assert summary.failed == 1
    assert summary.failed_medicine_names == ["Dolo 650"]
    assert summary.saved_successfully is False


def test_run_reaches_launch_pharma_through_login():
    invoice = make_invoice()
    automation = PurchaseAutomation()

    with patch.object(automation, "launch_pharma", return_value=True) as launch_pharma, \
        patch("app.automation.automation_engine.wait_for_window", return_value=True), \
        patch("app.automation.automation_engine.keyboard_controller.write", return_value=True), \
        patch("app.automation.automation_engine.keyboard_controller.press_enter", return_value=True), \
        patch.object(automation, "open_purchase_window", return_value=False), \
        patch("app.automation.automation_engine.get_import_logger"):
        summary = automation.run(invoice)

    launch_pharma.assert_called_once()
    assert summary.total_medicines == 1
    assert summary.imported_successfully == 0
    assert summary.failed == 1


def test_import_summary_generation():
    invoice = make_invoice()
    automation = PurchaseAutomation()
    start_time = datetime(2026, 8, 6, 10, 0, 0)
    import_result = ImportResult(
        total=1,
        success=0,
        failed=1,
        failed_items=invoice.items,
    )

    with patch("app.automation.automation_engine.datetime") as fake_datetime:
        fake_datetime.now.return_value = datetime(2026, 8, 6, 10, 0, 5)
        summary = automation._build_summary(invoice, import_result, start_time, False)

    assert summary.duration == 5
    assert summary.failed_medicine_names == ["Dolo 650"]


def test_run_receives_all_parsed_text_items():
    invoice = parse_invoice_text(
        """
Supplier: ABC Pharma
Invoice Number: INV-006
Invoice Date: 03-08-2026

Medicines:

Medicine 1
Item Description: A
Batch: B001
Expiry: 01-02-2028
Quantity: 1
MRP: 10

Medicine 2
Item Description: B
Batch: B002
Expiry: 01-02-2028
Quantity: 1
MRP: 10

Medicine 3
Item Description: C
Batch: B003
Expiry: 01-02-2028
Quantity: 1
MRP: 10

Medicine 4
Item Description: D
Batch: B004
Expiry: 01-02-2028
Quantity: 1
MRP: 10

Medicine 5
Item Description: E
Batch: B005
Expiry: 01-02-2028
Quantity: 1
MRP: 10

Medicine 6
Item Description: F
Batch: B006
Expiry: 01-02-2028
Quantity: 1
MRP: 10
"""
    )
    automation = PurchaseAutomation()
    import_result = ImportResult(total=6, success=6, failed=0, failed_items=[])

    with patch.object(automation, "login", return_value=True), \
        patch.object(automation, "open_purchase_window", return_value=True), \
        patch.object(automation, "fill_header", return_value=True) as fill_header, \
        patch.object(automation, "fill_items", return_value=import_result) as fill_items, \
        patch.object(automation, "save_purchase", return_value=True), \
        patch("app.automation.automation_engine.get_import_logger"):
        summary = automation.run(invoice)

    assert len(invoice.items) == 6
    fill_header.assert_called_once_with(invoice)
    fill_items.assert_called_once_with(invoice)
    assert summary.total_medicines == 6
    assert summary.imported_successfully == 6


if __name__ == "__main__":
    test_save_purchase_success_path()
    test_save_purchase_failure_path()
    test_run_complete_success_workflow()
    test_run_failure_summary_when_login_fails()
    test_run_reaches_launch_pharma_through_login()
    test_import_summary_generation()
    test_run_receives_all_parsed_text_items()
