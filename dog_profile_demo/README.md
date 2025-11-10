# Dog Profile Demo (Flask + SQLite)

A tiny web app to demonstrate:
- Python (Flask)
- SQLite database (view/edit with DB Browser for SQLite)
- Git for version control

## Quickstart

1) Create and activate a virtual environment (Windows PowerShell shown; adjust for Mac/Linux):
```
python -m venv .venv
.\.venv\Scripts\activate
```
Mac/Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies:
```
pip install -r requirements.txt
```

3) Initialize the database (creates `dogs.db` with sample data):
```
python init_db.py
```

4) Run the app:
```
python app.py
```
Visit http://127.0.0.1:5000

## What to Try

- Create a new dog profile (top-right button).
- Edit a dog, toggle friendly flags, change status.
- Use the search box and filter dropdowns.
- Open `dogs.db` in **DB Browser for SQLite** to see tables/rows change in real time.
- Use **Git** to track changes:
```
git init
git add .
git commit -m "Initial commit: Flask + SQLite dog demo"
```

## Files

- `app.py` – Flask routes + app setup
- `db.py` – helper for opening SQLite connection
- `init_db.py` – creates tables and seeds sample data
- `schema.sql` – SQL schema used by `init_db.py`
- `templates/` – HTML templates
- `static/styles.css` – minimal styling
- `requirements.txt` – Python dependencies

## Notes

This is a simple scaffold intended for a school assignment. It **does not** include authentication or advanced security.