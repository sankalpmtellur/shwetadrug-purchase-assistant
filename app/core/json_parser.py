import json

from app.core.csv_reader import convert_expiry, parse_decimal, validate_invoice, validate_item
from app.core.models import Invoice, InvoiceItem
from app.core.text_parser import normalize_key


HEADER_FIELDS = {
    "supplier": "supplier_name",
    "supplier name": "supplier_name",
    "supplier_name": "supplier_name",
    "invoice number": "invoice_number",
    "invoice no": "invoice_number",
    "invoice_number": "invoice_number",
    "invoice date": "invoice_date",
    "invoice_date": "invoice_date",
}

ITEM_FIELDS = {
    "name": "medicine_name",
    "item description": "medicine_name",
    "medicine": "medicine_name",
    "medicine name": "medicine_name",
    "medicine_name": "medicine_name",
    "batch": "batch_number",
    "batch number": "batch_number",
    "batch_number": "batch_number",
    "expiry": "expiry",
    "expiry date": "expiry",
    "expiry_date": "expiry",
    "quantity": "quantity",
    "qty": "quantity",
    "free": "free",
    "prate": "purchase_rate",
    "pts": "purchase_rate",
    "purchase rate": "purchase_rate",
    "purchase_rate": "purchase_rate",
    "mrp": "mrp",
    "srate": "sale_rate",
    "ptr": "sale_rate",
    "sale rate": "sale_rate",
    "sale_rate": "sale_rate",
    "discount": "discount_percent",
    "discount %": "discount_percent",
    "discount_percent": "discount_percent",
}

INVOICE_ROOT_KEYS = ("invoice", "purchase invoice", "purchase_invoice")
ITEM_LIST_KEYS = ("items", "medicines", "medicine list", "medicine details")


def parse_invoice_json(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        invoice = Invoice("", "", "")
        invoice.validation_errors.append(f"Invalid JSON: {error.msg}.")
        return invoice

    if not isinstance(data, dict):
        invoice = Invoice("", "", "")
        invoice.validation_errors.append("JSON invoice must be an object.")
        return invoice

    data = extract_invoice_object(data)
    header_data = extract_header_data(data)
    invoice = Invoice(
        supplier_name=header_data["supplier_name"],
        invoice_number=header_data["invoice_number"],
        invoice_date=header_data["invoice_date"],
    )

    for index, item_data in enumerate(extract_items(data), start=1):
        item = build_invoice_item(item_data)
        validate_item(item, index)
        invoice.items.append(item)

    validate_invoice(invoice)
    print(f"JSON invoice parsed: {len(invoice.items)} items")
    return invoice


def extract_invoice_object(data):
    for key, value in data.items():
        if normalize_key(key) in INVOICE_ROOT_KEYS and isinstance(value, dict):
            return value
    return data


def extract_header_data(data):
    header_data = {
        "supplier_name": "",
        "invoice_number": "",
        "invoice_date": "",
    }

    for key, value in data.items():
        field_name = HEADER_FIELDS.get(normalize_key(key))
        if field_name:
            header_data[field_name] = clean_json_value(value)

    return header_data


def extract_items(data):
    for key, value in data.items():
        if normalize_key(key) in ITEM_LIST_KEYS and isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def build_invoice_item(item_data):
    normalized_item = {}

    for key, value in item_data.items():
        field_name = ITEM_FIELDS.get(normalize_key(key))
        if field_name:
            normalized_item[field_name] = clean_json_value(value)

    return InvoiceItem(
        medicine_name=normalized_item.get("medicine_name", ""),
        batch_number=normalized_item.get("batch_number", ""),
        expiry=convert_expiry(normalized_item.get("expiry", "")),
        quantity=parse_decimal(normalized_item.get("quantity", "")),
        free=parse_decimal(normalized_item.get("free", ""), default_zero=True),
        purchase_rate=parse_decimal(normalized_item.get("purchase_rate", "")),
        mrp=parse_decimal(normalized_item.get("mrp", "")),
        sale_rate=parse_decimal(normalized_item.get("sale_rate", "")),
        discount_percent=parse_decimal(
            normalized_item.get("discount_percent", ""),
            default_zero=True,
        ),
    )


def clean_json_value(value):
    if value is None:
        return ""
    return str(value).strip()
