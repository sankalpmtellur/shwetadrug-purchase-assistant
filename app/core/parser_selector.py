from app.core.json_parser import parse_invoice_json
from app.core.text_parser import parse_invoice_text


STRUCTURED_TEXT = "Structured Text"
JSON = "JSON"
PARSER_CHOICES = (STRUCTURED_TEXT, JSON)


def parse_invoice_input(text, parser_name=STRUCTURED_TEXT):
    if parser_name == JSON:
        return parse_invoice_json(text)
    return parse_invoice_text(text)
