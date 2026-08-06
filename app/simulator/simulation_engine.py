from datetime import date, datetime


ACTION_DELAY_SECONDS = 0.1
SEARCH_DELAY_SECONDS = 1.5


def simulate(invoice):
    lines = build_simulation_lines(invoice)
    output = "\n".join(lines)
    print(output)
    return output


def build_simulation_lines(invoice):
    validation_errors = collect_validation_errors(invoice)
    estimated_actions = estimate_keyboard_actions(invoice)
    estimated_time = estimate_time_seconds(invoice, estimated_actions)

    lines = [
        "Launch Pharma",
        "✓",
        "",
        "Login",
        "✓",
        "",
        "Open Purchase Window",
        "✓",
        "",
        "Header",
        f"Date : {format_invoice_date(invoice.invoice_date)}",
        f"Supplier : {invoice.supplier_name}",
        f"Bill No : {invoice.invoice_number}",
        f"Today's Date : {format_today_date()}",
        "",
    ]

    for index, item in enumerate(invoice.items, start=1):
        lines.extend(build_medicine_lines(index, item))

    lines.extend(
        [
            "Summary",
            f"Supplier : {invoice.supplier_name}",
            f"Invoice Number : {invoice.invoice_number}",
            f"Medicines : {len(invoice.items)}",
            f"Estimated Keyboard Actions : {estimated_actions}",
            f"Estimated Time : {estimated_time:.1f} seconds",
            "",
            "Validation",
        ]
    )

    if validation_errors:
        lines.extend(f"- {error}" for error in validation_errors)
    else:
        lines.append("- None")

    return lines


def build_medicine_lines(index, item):
    return [
        f"Medicine {index}",
        "",
        "Select Medicine",
        format_value(item.medicine_name),
        "",
        "Batch",
        format_value(item.batch_number),
        "",
        "Expiry",
        format_value(item.expiry),
        "",
        "Qty",
        format_value(item.quantity),
        "",
        "Free",
        format_value(item.free),
        "",
        "PRate",
        format_value(item.purchase_rate),
        "",
        "MRP",
        format_value(item.mrp),
        "",
        "SRate",
        format_value(item.sale_rate),
        "",
        "Discount",
        format_value(item.discount_percent),
        "",
    ]


def collect_validation_errors(invoice):
    errors = []

    if not str(invoice.supplier_name).strip():
        errors.append("Missing supplier.")

    for index, item in enumerate(invoice.items, start=1):
        prefix = f"Medicine {index}"

        if not str(item.medicine_name).strip():
            errors.append(f"{prefix}: Missing medicine.")
        if not str(item.batch_number).strip():
            errors.append(f"{prefix}: Invalid batch.")
        if item.quantity is None:
            errors.append(f"{prefix}: Invalid quantity.")

    return errors


def estimate_keyboard_actions(invoice):
    header_actions = 11
    medicine_actions = 0

    for item in invoice.items:
        medicine_actions += len(str(item.medicine_name))
        medicine_actions += 1
        medicine_actions += count_entry_action(item.batch_number)
        medicine_actions += count_entry_action(item.expiry)
        medicine_actions += count_entry_action(item.quantity)
        medicine_actions += count_entry_action(item.free)
        medicine_actions += count_entry_action(item.purchase_rate)
        medicine_actions += count_entry_action(item.mrp)
        medicine_actions += count_entry_action(item.sale_rate)
        medicine_actions += count_entry_action(item.discount_percent)
        medicine_actions += 4

    return header_actions + medicine_actions


def count_entry_action(value):
    text = format_value(value)
    if text:
        return 2
    return 1


def estimate_time_seconds(invoice, keyboard_actions):
    search_characters = sum(len(str(item.medicine_name)) for item in invoice.items)
    search_characters += len(str(invoice.supplier_name))
    return (keyboard_actions * ACTION_DELAY_SECONDS) + (
        search_characters * SEARCH_DELAY_SECONDS
    )


def format_invoice_date(invoice_date):
    value = str(invoice_date).strip()
    if not value:
        return ""

    for date_format in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, date_format).strftime("%d/%m/%Y")
        except ValueError:
            continue

    return value.replace("-", "/")


def format_today_date():
    return date.today().strftime("%d/%m/%Y")


def format_value(value):
    if value is None:
        return ""
    return str(value).strip()
