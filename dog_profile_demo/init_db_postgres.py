import os
import psycopg
from psycopg.rows import dict_row

DDL = """
CREATE TABLE IF NOT EXISTS dogs (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  age INTEGER NOT NULL DEFAULT 0,
  size TEXT NOT NULL DEFAULT 'Medium',
  status TEXT NOT NULL DEFAULT 'Intake',
  kid_friendly BOOLEAN NOT NULL DEFAULT FALSE,
  cat_friendly BOOLEAN NOT NULL DEFAULT FALSE,
  dog_friendly BOOLEAN NOT NULL DEFAULT FALSE,
  notes TEXT NOT NULL DEFAULT '',
  image_url TEXT
);
"""

SEED = [
    ("Buddy", 2, "Medium", "Intake", True, False, True, "Sweet and energetic."),
    ("Molly", 7, "Small", "Fostered", True, True, True, "On thyroid meds."),
    ("Zeus", 4, "Large", "Hold", False, False, False, "Needs decompression."),
]

def run():
    url = os.environ["DATABASE_URL"]
    with psycopg.connect(url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute("SELECT COUNT(*) AS c FROM dogs;")
            if cur.fetchone()["c"] == 0:
                cur.executemany(
                    """
                    INSERT INTO dogs
                    (name, age, size, status, kid_friendly, cat_friendly, dog_friendly, notes)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    SEED,
                )
        conn.commit()
    print("Postgres ready.")

if __name__ == "__main__":
    run()

