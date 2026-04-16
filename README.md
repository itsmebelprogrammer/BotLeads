# BotLeads (CLI)

Minimal MVP CLI tool to extract business leads from **Google Maps** using **Selenium**, with export to **CSV/XLSX**.

The idea is simple: it collects **Name**, **Phone** (best-effort), **Website** (best-effort), and generates a **WhatsApp link** (`wa.me`) based on the normalized phone number.

---

## Features

- Searches Google Maps by term (e.g.: `"pizzaria Curitiba"`)
- Collects the following fields:
  - Name
  - Phone (best-effort)
  - Website (best-effort)
  - WhatsApp link (`wa.me`) based on normalized phone
- Exports to:
  - CSV (default)
  - XLSX (optional)

---

## Requirements

- Python 3.x or higher
- Google Chrome installed

---

## Installation

1) Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

2) Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

The CLI will prompt you for the search term and number of results.

---

## Output

The generated file will be saved in the project root with the name `leads.csv` (or `leads.xlsx` if XLSX export is enabled).

---

## License

This project is open source and available for study and portfolio purposes.
