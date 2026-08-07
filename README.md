# Purchase Assistant

Purchase Assistant is a Windows desktop automation assistant for importing purchase invoices into Pharma Ultimate. It accepts structured text or JSON input, previews the parsed invoice, validates the data, and then drives Pharma Ultimate through keyboard automation.

## Requirements

- Windows with Pharma Ultimate installed.
- Python 3.11 or newer.
- Pharma Ultimate executable path configured in `app/automation/config.py`.

## Installation

Create a virtual environment on Windows:

```cmd
python -m venv .venv
```

Activate it:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```cmd
pip install -r requirements.txt
```

## Running

Start the GUI:

```cmd
python main.py
```

You can also run:

```cmd
python run_gui.py
```

## Input Formats

Use the parser selector in the GUI:

- `Structured Text` for labelled text blocks.
- `JSON` for JSON invoices containing invoice fields and an `items` or `medicines` list.

Both parsers return the same internal `Invoice` object and use the same validation and automation flow.

## Verification

Run the automated test suite:

```cmd
python -m pytest
```

## Configuration

Common production values live in `app/automation/config.py`, including:

- Pharma Ultimate executable path.
- Window titles.
- Keyboard delays.
- Purchase-window navigation counts.
