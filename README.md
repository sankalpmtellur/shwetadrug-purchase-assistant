# Purchase Assistant

Purchase Assistant is a Windows desktop automation assistant built with Python. This repository currently contains only the base project structure and setup files that future automation features can build on.

## Folder Structure

```text
purchase-assistant/
├── app/
│   ├── automation/
│   ├── controllers/
│   ├── core/
│   ├── utils/
│   ├── config/
│   └── __init__.py
├── scripts/
├── screenshots/
├── logs/
├── tests/
├── requirements.txt
├── .gitignore
├── README.md
└── main.py
```

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

Run the application entry point:

```cmd
python main.py
```

Expected output:

```text
Purchase Assistant Started
```
