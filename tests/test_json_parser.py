from decimal import Decimal
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.json_parser import parse_invoice_json
from app.core.parser_selector import JSON, STRUCTURED_TEXT, parse_invoice_input
from tests.test_text_parser import SAMPLE_TEXT


SAMPLE_JSON = """
{
  "supplier": "Ajit Agencies",
  "invoice_number": "12345",
  "invoice_date": "03-08-2026",
  "items": [
    {
      "name": "Acenal P tablet",
      "batch": "11111",
      "expiry": "01-02-2028",
      "quantity": 30,
      "free": 0,
      "pts": 100,
      "mrp": 150,
      "ptr": 200,
      "discount": 10
    }
  ]
}
"""


def test_parse_invoice_json_matches_invoice_model():
    invoice = parse_invoice_json(SAMPLE_JSON)

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


def test_parser_selector_keeps_text_parser_working():
    text_invoice = parse_invoice_input(SAMPLE_TEXT, STRUCTURED_TEXT)
    json_invoice = parse_invoice_input(SAMPLE_JSON, JSON)

    assert text_invoice == json_invoice


def test_parse_invoice_json_validation_reuses_existing_rules():
    invoice = parse_invoice_json(
        """
{
  "invoice_number": "12345",
  "items": [
    {
      "name": "",
      "batch": "",
      "quantity": "abc",
      "mrp": "xyz"
    }
  ]
}
"""
    )

    assert "Supplier Name is required." in invoice.validation_errors
    assert "Row 1: Medicine Name is required." in invoice.validation_errors
    assert "Row 1: Batch Number is required." in invoice.validation_errors
    assert "Row 1: MRP must be numeric." in invoice.validation_errors
    assert "Row 1: Quantity must be numeric." in invoice.validation_errors


def test_parse_invoice_json_invalid_json_returns_validation_error():
    invoice = parse_invoice_json("{")

    assert "Invalid JSON:" in invoice.validation_errors[0]
