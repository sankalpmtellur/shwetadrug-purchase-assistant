from decimal import Decimal
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.text_parser import parse_invoice_text


SAMPLE_TEXT = """
Supplier:
Ajit Agencies

Invoice Number:
12345

Invoice Date:
03-08-2026

Medicines:

1.
Name: Acenal P tablet
Batch: 11111
Expiry: 01-02-2028
Quantity: 30
Free: 0
PRate: 100
MRP: 150
SRate: 200
Discount: 10
"""


def test_parse_invoice_text():
    invoice = parse_invoice_text(SAMPLE_TEXT)

    assert invoice.supplier_name == "Ajit Agencies"
    assert invoice.invoice_number == "12345"
    assert invoice.invoice_date == "03-08-2026"
    assert len(invoice.items) == 1

    item = invoice.items[0]
    assert item.medicine_name == "Acenal P tablet"
    assert item.batch_number == "11111"
    assert item.expiry == "01.02.28"
    assert item.quantity == Decimal("30")
    assert item.free == Decimal("0")
    assert item.purchase_rate == Decimal("100")
    assert item.mrp == Decimal("150")
    assert item.sale_rate == Decimal("200")
    assert item.discount_percent == Decimal("10")
    assert not invoice.validation_errors


def test_parse_invoice_text_validation_reuses_existing_rules():
    invoice = parse_invoice_text(
        """
Invoice Number:
12345

Medicines:

1.
Name:
Batch:
Expiry: 01-02-2028
Quantity: abc
MRP: xyz
"""
    )

    assert "Supplier Name is required." in invoice.validation_errors
    assert "Row 1: Medicine Name is required." in invoice.validation_errors
    assert "Row 1: Batch Number is required." in invoice.validation_errors
    assert "Row 1: MRP must be numeric." in invoice.validation_errors
    assert "Row 1: Quantity must be numeric." in invoice.validation_errors


if __name__ == "__main__":
    test_parse_invoice_text()
    test_parse_invoice_text_validation_reuses_existing_rules()
