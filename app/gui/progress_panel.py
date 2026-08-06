import tkinter as tk
from tkinter import ttk


class ProgressPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=(0, 12, 0, 0))
        self.status_var = tk.StringVar(value="Waiting...")
        self._build()

    def _build(self):
        self.progress = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 16))

        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.grid(row=0, column=1, sticky="e")

        self.columnconfigure(0, weight=1)

    def set_status(self, status):
        self.status_var.set(status)

    def set_progress(self, value):
        self.progress["value"] = value

    def reset(self):
        self.set_progress(0)
        self.set_status("Waiting...")
