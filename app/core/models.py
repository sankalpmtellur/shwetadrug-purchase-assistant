from dataclasses import dataclass, field
from datetime import datetime
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


@dataclass
class ImportResult:
    total: int
    success: int
    failed: int
    failed_items: list[InvoiceItem] = field(default_factory=list)


@dataclass
class ImportSummary:
    supplier: str
    invoice_number: str
    invoice_date: str
    total_medicines: int
    imported_successfully: int
    failed: int
    failed_medicine_names: list[str]
    start_time: datetime
    end_time: datetime
    duration: float
    saved_successfully: bool
