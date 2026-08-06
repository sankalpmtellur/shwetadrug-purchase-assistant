from decimal import Decimal
from pathlib import Path
import sys
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.automation_engine import (
    PurchaseAutomation,
    enter_if_not_blank,
    press_enters,
    select_medicine,
)
from app.core.models import Invoice, InvoiceItem


def make_item(name="Dolo 650"):
    return InvoiceItem(
        medicine_name=name,
        batch_number="B001",
        expiry="01.10.27",
        quantity=Decimal("10"),
        free=Decimal("1"),
        purchase_rate=Decimal("12.50"),
        mrp=Decimal("20.00"),
        sale_rate=Decimal("18.00"),
        discount_percent=Decimal("5"),
    )


def test_select_medicine_types_progressively_and_selects():
    with patch("app.automation.automation_engine.keyboard_controller.write", return_value=True) as write, \
        patch("app.automation.automation_engine.keyboard_controller.press_enter", return_value=True) as enter, \
        patch("app.automation.automation_engine.time.sleep", return_value=None), \
        patch("app.automation.automation_engine.is_medicine_highlighted", return_value=True):
        assert select_medicine("DOLO") is True
        assert [call.args[0] for call in write.call_args_list] == ["D", "O", "L", "O"]
        enter.assert_called_once()


def test_enter_helpers():
    with patch("app.automation.automation_engine.keyboard_controller.write", return_value=True) as write, \
        patch("app.automation.automation_engine.keyboard_controller.press_enter", return_value=True) as enter:
        assert enter_if_not_blank("ABC") is True
        assert enter_if_not_blank("") is True
        assert press_enters(4) is True
        write.assert_called_once_with("ABC")
        assert enter.call_count == 6


def test_fill_items_sequence():
    automation = PurchaseAutomation()
    invoice = Invoice("ABC Pharma", "INV-1001", "2026-08-06", items=[make_item()])

    with patch("app.automation.automation_engine.select_medicine", return_value=True) as medicine, \
        patch("app.automation.automation_engine.keyboard_controller.write", return_value=True) as write, \
        patch("app.automation.automation_engine.keyboard_controller.press_enter", return_value=True) as enter, \
        patch.object(automation, "verify_next_item_row_ready", return_value=True):
        result = automation.fill_items(invoice)

        assert result.total == 1
        assert result.success == 1
        assert result.failed == 0
        medicine.assert_called_once_with("Dolo 650")
        assert [call.args[0] for call in write.call_args_list] == [
            "B001",
            "01.10.27",
            "10",
            "1",
            "12.50",
            "20.00",
            "18.00",
            "5",
        ]
        assert enter.call_count == 14


def test_fill_items_failure_continues():
    automation = PurchaseAutomation()
    first_item = make_item("Missing Medicine")
    second_item = make_item("Dolo 650")
    invoice = Invoice(
        "ABC Pharma",
        "INV-1001",
        "2026-08-06",
        items=[first_item, second_item],
    )

    with patch(
        "app.automation.automation_engine.select_medicine",
        side_effect=[False, True],
    ), \
        patch("app.automation.automation_engine.keyboard_controller.write", return_value=True), \
        patch("app.automation.automation_engine.keyboard_controller.press_enter", return_value=True), \
        patch.object(automation, "verify_next_item_row_ready", return_value=True):
        result = automation.fill_items(invoice)

        assert result.total == 2
        assert result.success == 1
        assert result.failed == 1
        assert result.failed_items == [first_item]


if __name__ == "__main__":
    test_select_medicine_types_progressively_and_selects()
    test_enter_helpers()
    test_fill_items_sequence()
    test_fill_items_failure_continues()
