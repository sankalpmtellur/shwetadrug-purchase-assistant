from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.csv_reader import parse_invoice_csv


def test_parse_sample_csv():
    sample_path = Path(__file__).with_name("sample_invoice.csv")
    invoice = parse_invoice_csv(sample_path)

    print(invoice)

    assert invoice.supplier_name == "ABC Pharma Distributors"
    assert invoice.invoice_number == "INV-1001"
    assert invoice.invoice_date == "2026-08-06"
    assert len(invoice.items) == 2
    assert invoice.items[0].medicine_name == "Paracetamol 500mg"
    assert invoice.items[0].expiry == "01.10.27"
    assert not invoice.validation_errors


if __name__ == "__main__":
    test_parse_sample_csv()
