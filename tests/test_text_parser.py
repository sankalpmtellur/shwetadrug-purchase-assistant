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


def test_parse_invoice_text_requires_at_least_one_medicine():
    invoice = parse_invoice_text(
        """
Supplier:
Ajit Agencies

Invoice Number:
12345

Invoice Date:
03-08-2026
"""
    )

    assert len(invoice.items) == 0
    assert "At least one medicine is required." in invoice.validation_errors


def test_parse_real_world_text_with_six_medicines():
    invoice = parse_invoice_text(
        """
Supplier:
Narnkar & Co.

Invoice Number:
INV-006

Invoice Date:
03-08-2026

Medicine Details

Medicine 1
Item Description:
Acenal P tablet
Batch:
11111
Expiry:
01-02-2028
Quantity:
30
Free:
0
PRate:
100
MRP:
150
SRate:
200
Discount:
10

Medicine 2
Item Description: Dolo 650
Batch: B002
Expiry: 01-03-2028
Quantity: 20
Free: 0
PRate: 10
MRP: 15
SRate: 14
Discount: 5

Medicine 3
Item Description: Vitamin C
Batch: B003
Expiry: 01-04-2028
Quantity: 12
Free: 1
PRate: 50
MRP: 80
SRate: 75
Discount: 2

Medicine 4
Item Description: Zinc Tablet
Batch: B004
Expiry: 01-05-2028
Quantity: 15
Free: 0
PRate: 25
MRP: 40
SRate: 38
Discount: 0

Medicine 5
Item Description: Cough Syrup
Batch: B005
Expiry: 01-06-2028
Quantity: 8
Free: 0
PRate: 70
MRP: 95
SRate: 90
Discount: 3

Medicine 6
Item Description: Pain Relief Gel
Batch: B006
Expiry: 01-07-2028
Quantity: 5
Free: 0
PRate: 60
MRP: 85
SRate: 82
Discount: 4
"""
    )

    assert invoice.supplier_name == "Narnkar & Co."
    assert invoice.invoice_number == "INV-006"
    assert invoice.invoice_date == "03-08-2026"
    assert len(invoice.items) == 6
    assert invoice.items[0].medicine_name == "Acenal P tablet"
    assert invoice.items[0].batch_number == "11111"
    assert invoice.items[0].quantity == Decimal("30")
    assert invoice.items[5].medicine_name == "Pain Relief Gel"
    assert not invoice.validation_errors


if __name__ == "__main__":
    test_parse_invoice_text()
    test_parse_invoice_text_validation_reuses_existing_rules()
    test_parse_invoice_text_requires_at_least_one_medicine()
    test_parse_real_world_text_with_six_medicines()
