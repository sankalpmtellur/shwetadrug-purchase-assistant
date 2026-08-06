from app.core.csv_reader import convert_expiry, parse_decimal, validate_invoice, validate_item
from app.core.models import Invoice, InvoiceItem


HEADER_FIELDS = {
    "supplier": "supplier_name",
    "supplier name": "supplier_name",
    "invoice number": "invoice_number",
    "invoice no": "invoice_number",
    "invoice date": "invoice_date",
}

ITEM_FIELDS = {
    "name": "medicine_name",
    "medicine": "medicine_name",
    "medicine name": "medicine_name",
    "batch": "batch_number",
    "batch number": "batch_number",
    "expiry": "expiry",
    "expiry date": "expiry",
    "quantity": "quantity",
    "qty": "quantity",
    "free": "free",
    "prate": "purchase_rate",
    "purchase rate": "purchase_rate",
    "mrp": "mrp",
    "srate": "sale_rate",
    "sale rate": "sale_rate",
    "discount": "discount_percent",
    "discount %": "discount_percent",
}


def parse_invoice_text(text):
    header_data = {
        "supplier_name": "",
        "invoice_number": "",
        "invoice_date": "",
    }
    item_blocks = []
    current_item = None
    in_medicines_section = False
    pending_header_field = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if pending_header_field and ":" not in line:
            header_data[pending_header_field] = line
            pending_header_field = None
            continue

        if normalize_key(line.rstrip(":")) == "medicines":
            in_medicines_section = True
            pending_header_field = None
            continue

        if in_medicines_section and is_item_number(line):
            if current_item:
                item_blocks.append(current_item)
            current_item = {}
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        normalized_key = normalize_key(key)
        cleaned_value = value.strip()

        if in_medicines_section:
            if current_item is None:
                current_item = {}
            field_name = ITEM_FIELDS.get(normalized_key)
            if field_name:
                current_item[field_name] = cleaned_value
            continue

        field_name = HEADER_FIELDS.get(normalized_key)
        if field_name:
            if cleaned_value:
                header_data[field_name] = cleaned_value
            else:
                pending_header_field = field_name

    if current_item:
        item_blocks.append(current_item)

    invoice = Invoice(
        supplier_name=header_data["supplier_name"],
        invoice_number=header_data["invoice_number"],
        invoice_date=header_data["invoice_date"],
    )

    for index, item_data in enumerate(item_blocks, start=1):
        item = build_invoice_item(item_data)
        validate_item(item, index)
        invoice.items.append(item)

    validate_invoice(invoice)
    return invoice


def build_invoice_item(item_data):
    return InvoiceItem(
        medicine_name=item_data.get("medicine_name", ""),
        batch_number=item_data.get("batch_number", ""),
        expiry=convert_expiry(item_data.get("expiry", "")),
        quantity=parse_decimal(item_data.get("quantity", "")),
        free=parse_decimal(item_data.get("free", ""), default_zero=True),
        purchase_rate=parse_decimal(item_data.get("purchase_rate", "")),
        mrp=parse_decimal(item_data.get("mrp", "")),
        sale_rate=parse_decimal(item_data.get("sale_rate", "")),
        discount_percent=parse_decimal(item_data.get("discount_percent", ""), default_zero=True),
    )


def is_item_number(line):
    value = line.rstrip(".").strip()
    return value.isdigit()


def normalize_key(value):
    return " ".join(str(value).strip().lower().replace("_", " ").split())
