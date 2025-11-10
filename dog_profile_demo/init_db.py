import sqlite3, os
from pathlib import Path

DB_PATH = "dogs.db"

def run():
    # Load schema
    with open("schema.sql", "r", encoding="utf-8") as f:
        schema = f.read()
    # Create db and apply schema
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)

    # Seed some sample rows
    dogs = [
        ("Buddy", 2, "Medium", "Intake", 1, 0, 1, "Sweet and energetic. Microchip pending."),
        ("Molly", 7, "Small", "Fostered", 1, 1, 1, "On thyroid meds. Great with kids."),
        ("Zeus", 4, "Large", "Hold", 0, 0, 0, "Needs decompression. No cats."),
    ]
    conn.executemany(
        "INSERT INTO dogs (name, age, size, status, kid_friendly, cat_friendly, dog_friendly, notes) VALUES (?,?,?,?,?,?,?,?)",
        dogs
    )
    conn.commit()
    conn.close()
    print("Initialized dogs.db with sample data.")

if __name__ == "__main__":
    run()