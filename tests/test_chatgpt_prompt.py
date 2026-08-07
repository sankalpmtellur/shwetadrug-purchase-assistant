from pathlib import Path
import sys
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.chatgpt_prompt import CHATGPT_PROMPT
from app.gui.main_window import PurchaseAssistantWindow


class ClipboardWindow:
    def __init__(self):
        self.clipboard_value = "old"
        self.updated = False

    def clipboard_clear(self):
        self.clipboard_value = ""

    def clipboard_append(self, value):
        self.clipboard_value += value

    def update(self):
        self.updated = True


def test_chatgpt_prompt_contains_official_extraction_format():
    assert "Extract the purchase invoice into the EXACT format below." in CHATGPT_PROMPT
    assert "Return ONLY the structured text below." in CHATGPT_PROMPT
    assert "SUPPLIER: <Supplier Name>" in CHATGPT_PROMPT
    assert "INVOICE_NO: <Invoice Number>" in CHATGPT_PROMPT
    assert "INVOICE_DATE: <DD-MM-YYYY>" in CHATGPT_PROMPT
    assert "PRATE: ..." in CHATGPT_PROMPT
    assert "SRATE: ..." in CHATGPT_PROMPT


def test_copy_chatgpt_prompt_copies_prompt_and_shows_success_message():
    window = ClipboardWindow()

    with patch("app.gui.main_window.messagebox.showinfo") as showinfo:
        PurchaseAssistantWindow.copy_chatgpt_prompt(window)

    assert window.clipboard_value == CHATGPT_PROMPT
    assert window.updated is True
    showinfo.assert_called_once_with(
        "Copy ChatGPT Prompt",
        "ChatGPT prompt copied to clipboard.",
    )
