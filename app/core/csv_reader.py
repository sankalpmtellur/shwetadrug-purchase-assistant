import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.core.models import Invoice, InvoiceItem


SUPPORTED_ENCODINGS = ("utf-8-sig", "utf-16", "utf-8")

HEADER_ALIASES = {
    "supplier_name": ("supplier name", "supplier", "party name", "vendor name"),
    "invoice_number": ("invoice number", "invoice no", "invoice no.", "inv no", "bill no"),
    "invoice_date": ("invoice date", "bill date", "date"),
}

ITEM_ALIASES = {
    "medicine_name": ("medicine name", "medicine", "item name", "product name", "name"),
    "batch_number": ("batch number", "batch no", "batch no.", "batch"),
    "expiry": ("expiry", "expiry date", "exp", "exp date"),
    "quantity": ("quantity", "qty"),
    "free": ("free", "free qty", "free quantity"),
    "purchase_rate": ("purchase rate", "ptr", "p rate", "rate"),
    "mrp": ("mrp",),
    "sale_rate": ("sale rate", "sales rate", "s rate"),
    "discount_percent": ("discount %", "discount", "disc %", "disc"),
}


def detect_encoding(file_path):
    path = Path(file_path)

    for encoding in SUPPORTED_ENCODINGS:
        try:
            path.read_text(encoding=encoding)
            return encoding
        except UnicodeError:
            continue

    raise UnicodeError(f"Unable to read CSV with supported encodings: {SUPPORTED_ENCODINGS}")


def read_csv_rows(file_path):
    path = Path(file_path)
    encoding = detect_encoding(path)

    with path.open("r", encoding=encoding, newline="") as csv_file:
        return list(csv.reader(csv_file)), encoding


def convert_expiry(expiry):
    value = clean_value(expiry)
    if not value:
        return ""

    parts = value.replace("-", "/").replace(".", "/").split("/")
    if len(parts) == 2:
        month, year = parts
        return f"01.{month.zfill(2)}.{year[-2:]}"

    if len(parts) == 3:
        day, month, year = parts
        return f"{day.zfill(2)}.{month.zfill(2)}.{year[-2:]}"

    return value


def parse_invoice_csv(file_path):
    rows, _encoding = read_csv_rows(file_path)
    normalized_rows = [row for row in rows if any(clean_value(cell) for cell in row)]
    header_index = find_item_header_index(normalized_rows)

    if header_index is None:
        invoice = Invoice("", "", "")
        invoice.validation_errors.append("Could not find item table header row.")
        print_invoice_summary(invoice)
        return invoice

    metadata = parse_metadata(normalized_rows[:header_index])
    item_headers = normalized_rows[header_index]
    item_rows = normalized_rows[header_index + 1 :]

    invoice = Invoice(
        supplier_name=metadata.get("supplier_name", ""),
        invoice_number=metadata.get("invoice_number", ""),
        invoice_date=metadata.get("invoice_date", ""),
    )

    for row_number, row in enumerate(item_rows, start=header_index + 2):
        row_data = map_row(item_headers, row)

        if not invoice.supplier_name:
            invoice.supplier_name = get_field(row_data, "supplier_name", HEADER_ALIASES)
        if not invoice.invoice_number:
            invoice.invoice_number = get_field(row_data, "invoice_number", HEADER_ALIASES)
        if not invoice.invoice_date:
            invoice.invoice_date = get_field(row_data, "invoice_date", HEADER_ALIASES)

        item = parse_item(row_data, row_number)
        if item:
            invoice.items.append(item)

    validate_invoice(invoice)
    print_invoice_summary(invoice)
    return invoice


def find_item_header_index(rows):
    for index, row in enumerate(rows):
        normalized = {normalize_header(cell) for cell in row}
        has_medicine = any(alias in normalized for alias in ITEM_ALIASES["medicine_name"])
        has_batch = any(alias in normalized for alias in ITEM_ALIASES["batch_number"])
        if has_medicine and has_batch:
            return index
    return None


def parse_metadata(rows):
    metadata = {}

    for row in rows:
        if len(row) < 2:
            continue

        key = normalize_header(row[0])
        value = clean_value(row[1])

        for field_name, aliases in HEADER_ALIASES.items():
            if key in aliases and value:
                metadata[field_name] = value

    return metadata


def map_row(headers, row):
    row_data = {}

    for index, header in enumerate(headers):
        row_data[normalize_header(header)] = clean_value(row[index]) if index < len(row) else ""

    return row_data


def parse_item(row_data, row_number):
    medicine_name = get_item_value(row_data, "medicine_name")
    batch_number = get_item_value(row_data, "batch_number")

    if not medicine_name and not batch_number:
        return None

    item = InvoiceItem(
        medicine_name=medicine_name,
        batch_number=batch_number,
        expiry=convert_expiry(get_item_value(row_data, "expiry")),
        quantity=parse_decimal(get_item_value(row_data, "quantity")),
        free=parse_decimal(get_item_value(row_data, "free"), default_zero=True),
        purchase_rate=parse_decimal(get_item_value(row_data, "purchase_rate")),
        mrp=parse_decimal(get_item_value(row_data, "mrp")),
        sale_rate=parse_decimal(get_item_value(row_data, "sale_rate")),
        discount_percent=parse_decimal(
            get_item_value(row_data, "discount_percent"), default_zero=True
        ),
    )

    validate_item(item, row_number)
    return item


def validate_invoice(invoice):
    if not invoice.supplier_name:
        invoice.validation_errors.append("Supplier Name is required.")

    for item in invoice.items:
        invoice.validation_errors.extend(item.validation_errors)


def validate_item(item, row_number):
    prefix = f"Row {row_number}:"

    if not item.medicine_name:
        item.validation_errors.append(f"{prefix} Medicine Name is required.")
    if not item.batch_number:
        item.validation_errors.append(f"{prefix} Batch Number is required.")
    if item.mrp is None:
        item.validation_errors.append(f"{prefix} MRP must be numeric.")
    if item.quantity is None:
        item.validation_errors.append(f"{prefix} Quantity must be numeric.")


def parse_decimal(value, default_zero=False):
    cleaned = clean_value(value).replace(",", "")

    if not cleaned and default_zero:
        return Decimal("0")
    if not cleaned:
        return None

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def get_item_value(row_data, field_name):
    aliases = ITEM_ALIASES[field_name]
    return get_field(row_data, field_name, {field_name: aliases})


def get_field(row_data, field_name, aliases_by_field):
    for alias in aliases_by_field[field_name]:
        value = row_data.get(alias, "")
        if value:
            return value
    return ""


def clean_value(value):
    return str(value).strip() if value is not None else ""


def normalize_header(value):
    return " ".join(clean_value(value).lower().replace("_", " ").split())


def print_invoice_summary(invoice):
    print(f"Supplier: {invoice.supplier_name}")
    print(f"Invoice No: {invoice.invoice_number}")
    print(f"Invoice Date: {invoice.invoice_date}")
    print(f"Total Medicines: {len(invoice.items)}")
    print("Validation Errors:")

    if invoice.validation_errors:
        for error in invoice.validation_errors:
            print(f"- {error}")
    else:
        print("- None")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m app.core.csv_reader <csv-file>")
    else:
        parse_invoice_csv(sys.argv[1])
