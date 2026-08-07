import tkinter as tk
import threading
import traceback
from tkinter import messagebox, ttk

from app.automation.automation_engine import PurchaseAutomation
from app.core.chatgpt_prompt import CHATGPT_PROMPT
from app.core.parser_selector import PARSER_CHOICES, STRUCTURED_TEXT, parse_invoice_input
from app.gui.preview_panel import PreviewPanel
from app.gui.progress_panel import ProgressPanel


class PurchaseAssistantWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Purchase Assistant")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.current_invoice = None
        self.parser_var = tk.StringVar(value=STRUCTURED_TEXT)
        self.is_import_running = False
        self.automation = PurchaseAutomation(progress_callback=self.handle_progress)

        self._configure_styles()
        self._build()

    def _configure_styles(self):
        self.configure(bg="#f5f7fa")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f5f7fa")
        style.configure("Panel.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("TLabel", background="#f5f7fa", foreground="#1f2933", font=("Segoe UI", 10))
        style.configure("Heading.TLabel", font=("Segoe UI", 22, "bold"), background="#f5f7fa")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground="#52606d", background="#f5f7fa")
        style.configure("PanelTitle.TLabel", font=("Segoe UI", 13, "bold"), background="#ffffff")
        style.configure("TButton", font=("Segoe UI", 10), padding=(14, 8))
        style.configure("Emergency.TButton", foreground="#8a1f11")

    def _build(self):
        container = ttk.Frame(self, padding=24)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ttk.Label(header, text="Purchase Assistant", style="Heading.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
        )
        ttk.Label(
            header,
            text="Import medicines into Pharma Ultimate",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        content = ttk.Frame(container)
        content.grid(row=1, column=0, sticky="nsew")

        input_panel = ttk.Frame(content, style="Panel.TFrame", padding=16)
        input_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        input_header = ttk.Frame(input_panel, style="Panel.TFrame")
        input_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(input_header, text="Paste ChatGPT Output", style="PanelTitle.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
        )

        ttk.Button(
            input_header,
            text="Copy ChatGPT Prompt",
            command=self.copy_chatgpt_prompt,
        ).grid(row=0, column=1, padx=(12, 0), sticky="e")

        parser_selector = ttk.Combobox(
            input_header,
            textvariable=self.parser_var,
            values=PARSER_CHOICES,
            state="readonly",
            width=18,
        )
        parser_selector.grid(row=0, column=2, sticky="e", padx=(12, 0))
        input_header.columnconfigure(0, weight=1)

        self.input_text = tk.Text(
            input_panel,
            wrap="word",
            bg="#ffffff",
            fg="#1f2933",
            insertbackground="#1f2933",
            relief="solid",
            borderwidth=1,
            font=("Consolas", 10),
        )
        self.input_text.grid(row=1, column=0, sticky="nsew")

        preview_container = ttk.Frame(content, style="Panel.TFrame")
        preview_container.grid(row=0, column=1, sticky="nsew")
        self.preview_panel = PreviewPanel(preview_container)
        self.preview_panel.pack(fill="both", expand=True)

        button_row = ttk.Frame(container)
        button_row.grid(row=2, column=0, sticky="ew", pady=(18, 0))

        ttk.Button(button_row, text="Preview", command=self.preview_invoice).grid(
            row=0,
            column=0,
            padx=(0, 10),
        )
        ttk.Button(button_row, text="Start Import", command=self.start_import).grid(
            row=0,
            column=1,
            padx=(0, 10),
        )
        ttk.Button(button_row, text="Clear", command=self.clear).grid(
            row=0,
            column=2,
            padx=(0, 10),
        )
        ttk.Button(
            button_row,
            text="Emergency Stop",
            command=self.emergency_stop,
            style="Emergency.TButton",
        ).grid(row=0, column=3)

        self.progress_panel = ProgressPanel(container)
        self.progress_panel.grid(row=3, column=0, sticky="ew")

        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)
        input_panel.columnconfigure(0, weight=1)
        input_panel.rowconfigure(1, weight=1)

    def preview_invoice(self):
        pasted_text = self.input_text.get("1.0", tk.END).strip()
        if not pasted_text:
            messagebox.showinfo("Preview", "Paste structured text before previewing.")
            return

        self.current_invoice = parse_invoice_input(pasted_text, self.parser_var.get())
        self.preview_panel.display_invoice(self.current_invoice)
        self.progress_panel.set_progress(0)
        self.progress_panel.set_status("Preview Ready")

    def copy_chatgpt_prompt(self):
        self.clipboard_clear()
        self.clipboard_append(CHATGPT_PROMPT)
        self.update()
        messagebox.showinfo(
            "Copy ChatGPT Prompt",
            "ChatGPT prompt copied to clipboard.",
        )

    def start_import(self):
        print("[GUI] Start Import clicked")
        if self.is_import_running:
            messagebox.showinfo("Start Import", "Import is already running.")
            return

        if self.current_invoice is None:
            self.preview_invoice()

        if self.current_invoice is None:
            return

        print("[GUI] Invoice object received")
        print(f"[GUI] Invoice has {len(self.current_invoice.items)} items")

        if self.current_invoice.validation_errors:
            print("[GUI] Validation failed before automation")
            messagebox.showerror(
                "Validation Failed",
                "\n".join(self.current_invoice.validation_errors),
            )
            self.progress_panel.set_status("Validation Failed")
            return

        self.is_import_running = True
        self.progress_panel.set_progress(0)
        self.progress_panel.set_status("Preparing...")

        thread = threading.Thread(
            target=self._run_import,
            args=(self.current_invoice,),
            daemon=True,
        )
        thread.start()

    def clear(self):
        self.input_text.delete("1.0", tk.END)
        self.current_invoice = None
        self.preview_panel.clear()
        self.progress_panel.reset()

    def emergency_stop(self):
        self.automation.stop()
        self.progress_panel.set_status("Automation Stopped")

    def handle_progress(self, status, value=None):
        self.after(0, self._apply_progress, status, value)

    def _apply_progress(self, status, value=None):
        self.progress_panel.set_status(status)
        if value is not None:
            self.progress_panel.set_progress(value)

    def _run_import(self, invoice):
        try:
            print("[GUI] Worker entered")
            print("[GUI] Calling PurchaseAutomation.run()")
            summary = self.automation.run(invoice)
            print("[GUI] PurchaseAutomation.run() returned")
        except Exception as error:
            traceback.print_exc()
            self.after(0, self._show_import_error, error)
            return

        self.after(0, self._show_completion, summary)

    def _show_import_error(self, error):
        self.is_import_running = False
        self.progress_panel.set_status("Import Failed")
        messagebox.showerror("Import Failed", str(error))

    def _show_completion(self, summary):
        self.is_import_running = False

        if self.automation.stop_requested:
            self.progress_panel.set_status("Automation Stopped")
            messagebox.showinfo("Automation Stopped", "Automation Stopped")
            return

        duration_text = format_duration(summary.duration)
        self.progress_panel.set_status("Completed")
        self.progress_panel.set_progress(100)
        messagebox.showinfo(
            "Import Completed",
            "Import Completed\n\n"
            f"Imported: {summary.imported_successfully}\n"
            f"Failed: {summary.failed}\n"
            f"Duration: {duration_text}",
        )


def format_duration(seconds):
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60

    if minutes:
        return f"{minutes}m {remaining_seconds}s"
    return f"{remaining_seconds}s"
