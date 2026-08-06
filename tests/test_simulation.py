from decimal import Decimal
from io import StringIO
from pathlib import Path
import sys
from contextlib import redirect_stdout
from unittest.mock import Mock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.models import Invoice, InvoiceItem
from app.simulator.simulation_engine import collect_validation_errors, simulate


def make_invoice():
    item = InvoiceItem(
        medicine_name="DOLO 650 TAB",
        batch_number="AB1234",
        expiry="01.10.27",
        quantity=Decimal("10"),
        free=Decimal("0"),
        purchase_rate=Decimal("11.25"),
        mrp=Decimal("15.00"),
        sale_rate=Decimal("14.00"),
        discount_percent=Decimal("12"),
    )
    return Invoice(
        supplier_name="CIPLA",
        invoice_number="24563",
        invoice_date="2026-08-03",
        items=[item],
    )


def test_simulate_printed_workflow():
    fake_date = Mock()
    fake_date.today.return_value.strftime.return_value = "06/08/2026"

    printed_buffer = StringIO()
    with patch("app.simulator.simulation_engine.date", fake_date), redirect_stdout(
        printed_buffer
    ):
        output = simulate(make_invoice())

    printed = printed_buffer.getvalue()

    assert "Launch Pharma" in printed
    assert "Login" in printed
    assert "Open Purchase Window" in printed
    assert "Header" in printed
    assert "Date : 03/08/2026" in output
    assert "Supplier : CIPLA" in output
    assert "Bill No : 24563" in output
    assert "Today's Date : 06/08/2026" in output
    assert "Medicine 1" in output
    assert "DOLO 650 TAB" in output
    assert "Batch\nAB1234" in output
    assert "Estimated Keyboard Actions" in output
    assert "Estimated Time" in output
    assert "Validation\n- None" in output


def test_validation_errors():
    invoice = Invoice(
        supplier_name="",
        invoice_number="24563",
        invoice_date="2026-08-03",
        items=[
            InvoiceItem(
                medicine_name="",
                batch_number="",
                expiry="01.10.27",
                quantity=None,
                free=Decimal("0"),
                purchase_rate=Decimal("11.25"),
                mrp=Decimal("15.00"),
                sale_rate=Decimal("14.00"),
                discount_percent=Decimal("12"),
            )
        ],
    )

    errors = collect_validation_errors(invoice)

    assert "Missing supplier." in errors
    assert "Medicine 1: Missing medicine." in errors
    assert "Medicine 1: Invalid batch." in errors
    assert "Medicine 1: Invalid quantity." in errors


if __name__ == "__main__":
    test_simulate_printed_workflow()
    test_validation_errors()
