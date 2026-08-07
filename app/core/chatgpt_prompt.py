CHATGPT_PROMPT = """Extract the purchase invoice into the EXACT format below.

Rules:

1. Do NOT skip any medicine.
2. Keep medicine names exactly as printed.
3. Keep batch numbers exactly as printed.
4. Invoice Date format: DD-MM-YYYY.
5. Expiry format: DD-MM-YYYY (Example: 01-05-2028).
6. Quantity = invoice quantity.
7. Free = invoice free quantity (use 0 if not present).
8. PRATE = PTS column.
9. MRP = MRP column.
10. SRATE = PTR column.
11. DISCOUNT = Discount column (use 0.00 if not present).
12. Please send me the data in copy-pastable format only.
13. Return ONLY the structured text below.
14. Do NOT add explanations, markdown, code blocks, or any extra text.

Format:

SUPPLIER: <Supplier Name>
INVOICE_NO: <Invoice Number>
INVOICE_DATE: <DD-MM-YYYY>

ITEMS

1.
NAME: ...
BATCH: ...
EXPIRY: ...
QTY: ...
FREE: ...
PRATE: ...
MRP: ...
SRATE: ...
DISCOUNT: ...

2.
...

Continue until every medicine from the invoice has been extracted."""
