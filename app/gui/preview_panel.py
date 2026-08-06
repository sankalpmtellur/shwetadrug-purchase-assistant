import tkinter as tk
from tkinter import ttk


class PreviewPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=16)
        self.summary_vars = {
            "Supplier": tk.StringVar(value=""),
            "Invoice Number": tk.StringVar(value=""),
            "Invoice Date": tk.StringVar(value=""),
            "Total Medicines": tk.StringVar(value=""),
        }
        self.validation_var = tk.StringVar(value="")
        self._build()

    def _build(self):
        title = ttk.Label(self, text="Invoice Preview", style="PanelTitle.TLabel")
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        for index, (label, variable) in enumerate(self.summary_vars.items(), start=1):
            ttk.Label(self, text=f"{label}:").grid(row=index, column=0, sticky="nw", pady=4)
            ttk.Label(self, textvariable=variable, wraplength=300).grid(
                row=index,
                column=1,
                sticky="nw",
                pady=4,
                padx=(12, 0),
            )

        validation_label = ttk.Label(self, text="Validation Errors:")
        validation_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=(18, 4))

        self.validation_text = tk.Text(
            self,
            height=10,
            wrap="word",
            bg="#ffffff",
            fg="#1f2933",
            relief="solid",
            borderwidth=1,
            state="disabled",
        )
        self.validation_text.grid(row=6, column=0, columnspan=2, sticky="nsew")

        self.columnconfigure(1, weight=1)
        self.rowconfigure(6, weight=1)

    def clear(self):
        for variable in self.summary_vars.values():
            variable.set("")
        self._set_validation_text("")

    def display_invoice(self, invoice):
        self.summary_vars["Supplier"].set(invoice.supplier_name)
        self.summary_vars["Invoice Number"].set(invoice.invoice_number)
        self.summary_vars["Invoice Date"].set(invoice.invoice_date)
        self.summary_vars["Total Medicines"].set(str(len(invoice.items)))

        if invoice.validation_errors:
            validation_text = "\n".join(f"- {error}" for error in invoice.validation_errors)
        else:
            validation_text = "None"

        self._set_validation_text(validation_text)

    def _set_validation_text(self, value):
        self.validation_text.configure(state="normal")
        self.validation_text.delete("1.0", tk.END)
        self.validation_text.insert("1.0", value)
        self.validation_text.configure(state="disabled")
