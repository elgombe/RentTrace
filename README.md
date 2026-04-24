# RentTrace

> Forensic rental income reconciliation system for auditors.

RentTrace is a Windows desktop application that reconstructs expected rental income, verifies transactions against bank statements and receipts, flags financial discrepancies, and generates audit-ready PDF reports

---

## Screenshots

| Dashboard | Tenants | Upload |
|---|---|---|
| <img src='./app/static/icons/Screenshot 2026-04-24 110353.png'> | <img src='./app/static/icons/Screenshot 2026-04-24 110407.png'> | <img src='./app/static/icons/Screenshot 2026-04-24 110420.png'> |

---

## What It Does

| Feature | Description |
|---|---|
| Income reconstruction | Calculates expected monthly rent per tenant from lease records |
| Bank statement import | Parses CSV or Excel bank files, stores all transactions |
| Receipt import | Imports receipt registers and auto-matches tenants by name |
| Reconciliation engine | Compares expected income vs receipts vs bank deposits |
| Discrepancy flagging | Flags missing deposits, unverified income, and arrears |
| PDF report export | Generates a formatted audit report for each period |
| Authentication | Email + password login with bcrypt-hashed credentials |

---

## Reconciliation Rules

The matching engine applies four rules per tenant per period:

```
Rule 1 — MATCHED         Receipt amount = bank deposit (within $1.00 tolerance)
Rule 2 — MISSING DEPOSIT Receipt exists but no matching bank deposit found
Rule 3 — UNVERIFIED      Bank deposit exists but no receipt to explain it
Rule 4 — ARREARS         Expected rent with no receipt and no bank deposit
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop window | PyWebView |
| Web framework | Flask |
| Database ORM | Flask-SQLAlchemy + SQLite |
| Frontend | Bulma CSS + HTMX |
| Charts | Chart.js |
| File parsing | Pandas + openpyxl |
| PDF export | ReportLab |
| Auth | bcrypt |
| Packaging | PyInstaller |

---

## Project Structure

```
RentTrace/
├── main.py                          # Entry point — starts Flask + PyWebView
├── config.py                        # App settings, DB path, upload folder
├── requirements.txt                 # Python dependencies
├── RentTrace.spec                   # PyInstaller build spec
├── README.md
│
└── app/
    ├── __init__.py                  # Flask app factory
    ├── views.py                     # Page route blueprint (via api/views.py)
    │
    ├── api/                         # HTTP layer — blueprints only
    │   ├── auth.py                  # POST /api/auth/login, logout, me
    │   ├── tenants.py               # CRUD /api/tenants
    │   ├── transactions.py          # POST /api/transactions/upload
    │   ├── receipts.py              # POST /api/receipts/upload
    │   ├── reconcile.py             # POST /api/reconcile/run + results
    │   ├── reports.py               # GET  /api/reports/export
    │   └── views.py                 # Page routes (login, dashboard, etc.)
    │
    ├── controllers/                 # Business logic layer
    │   ├── auth_controller.py       # Login, password hashing, registration
    │   ├── tenant_controller.py     # Tenant CRUD with validation
    │   ├── upload_controller.py     # CSV/Excel parsing with pandas
    │   ├── reconcile_controller.py  # Core matching engine + summary stats
    │   └── report_controller.py     # PDF generation with ReportLab
    │
    ├── models/                      # Database layer — SQLAlchemy models
    │   ├── database.py              # db instance + init_db + default user seed
    │   ├── user_model.py            # User table
    │   ├── tenant_model.py          # Tenant table
    │   ├── transaction_model.py     # BankTransaction table
    │   ├── receipt_model.py         # Receipt table
    │   └── reconciliation_model.py  # Reconciliation results table
    │
    ├── middleware/
    │   └── auth_guard.py            # @login_required decorator + get_current_user()
    │
    ├── views/                       # Jinja2 HTML templates
    │   ├── base.html                # Layout shell — sidebar, topbar, flash
    │   ├── login.html               # Standalone login page
    │   ├── dashboard.html           # Summary cards + charts
    │   ├── tenants.html             # Tenant list + add/edit modal
    │   ├── upload.html              # Drag-and-drop file upload
    │   ├── reconcile.html           # Run reconciliation + results table
    │   └── partials/                # HTMX fragments (table swaps)
    │       ├── tenants_table.html
    │       ├── transactions_table.html
    │       ├── receipts_table.html
    │       ├── reconcile_table.html
    │       └── exceptions_table.html
    │
    └── static/
        ├── js/
        │   ├── htmx.min.js          # Bundled locally — no CDN dependency
        │   └── charts.js
        ├── css/
        │   └── style.css
        └── icons/
            ├── renttrace.ico        # Multi-resolution icon (16–256px)
            └── renttrace.png        # Source PNG
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/elgombe/RentTrace.git
cd RentTrace
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python main.py
```

The app opens as a native Windows window. On first run, the database is created automatically and the default user is seeded.

### 4. Log in

```
Email:    admin@rentrace.co.zw
Password: admin123
```

> **Change the default password after first login.**

---

## Testing the System

Sample test files are included in the repository:

| File | Purpose |
|---|---|
| `Tenants_Register.xlsx` | Import via Tenants page |
| `Bank_Statement_Jan_Jun_2025.xlsx` | Upload via Upload page → Bank statement |
| `Receipts_Register_Jan_Jun_2025.xlsx` | Upload via Upload page → Receipts |
| `Test_Scenarios_Cheatsheet.xlsx` | Expected reconciliation results |

### Expected test results

| Scenario | Tenant | Month | Expected flag |
|---|---|---|---|
| Normal payment | All tenants | Jan, Feb, Apr, Jun | Matched |
| Missing deposit | James Moyo | March 2025 | Missing deposit |
| Unverified cash | Unknown | April 2025 | Unverified income |
| Arrears | Sí Ncube | May 2025 | Arrears |
| Overpayment | Farai Mutasa | February 2025 | Matched (overpayment noted) |
| Non-rent deposits | Various | All months | Unverified income |

Run reconciliation per period — start with `2025-01`, then step through to `2025-06`.


## Default Configuration

| Setting | Value |
|---|---|
| Host | 127.0.0.1 (localhost only) |
| Port | 5000 |
| Database | `data/renttrace.db` |
| Upload folder | `data/uploads/` |
| Session lifetime | 8 hours |
| Max upload size | 16 MB |
| Bcrypt rounds | 12 |

---

## Dependencies

```
flask>=3.0.0
flask-sqlalchemy>=3.1.0
pywebview>=5.0.0
bcrypt>=4.0.0
pandas>=2.0.0
openpyxl>=3.1.0
reportlab>=4.0.0
pyinstaller>=6.0.0
```

---

## Security Notes

- Passwords are stored as bcrypt hashes — never plain text
- All routes are protected by `@login_required` except `/login`
- Flask runs on `127.0.0.1` only — not accessible from the network
- Session expires after 8 hours of inactivity
- Change `SECRET_KEY` in `config.py` before distributing to client

---


&copy; 2026 RentTrace