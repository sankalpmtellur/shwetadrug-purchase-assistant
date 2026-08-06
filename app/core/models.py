from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class InvoiceItem:
    medicine_name: str
    batch_number: str
    expiry: str
    quantity: Decimal | None
    free: Decimal | None
    purchase_rate: Decimal | None
    mrp: Decimal | None
    sale_rate: Decimal | None
    discount_percent: Decimal | None
    validation_errors: list[str] = field(default_factory=list)


@dataclass
class Invoice:
    supplier_name: str
    invoice_number: str
    invoice_date: str
    items: list[InvoiceItem] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
