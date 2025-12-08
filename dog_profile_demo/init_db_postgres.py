# dog_profile_demo/init_db_postgres.py
import os
import psycopg
from psycopg.rows import dict_row

DDL = """
CREATE TABLE IF NOT EXISTS dogs (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  age INT NOT NULL,
  size TEXT NOT NULL,
  status TEXT NOT NULL,
  kid_friendly INT NOT NULL DEFAULT 0,
  cat_friendly INT NOT NULL DEFAULT 0,
  dog_friendly INT NOT NULL DEFAULT 0,
  notes TEXT,
  image_url TEXT
);
"""

SEED = [
    ("Buddy", 2, "Medium", "Intake", 1, 0, 1, "Sweet and energetic."),
    ("Molly", 7, "Small", "Fostered", 1, 1, 1, "On thyroid meds."),
    ("Zeus", 4, "Large", "Hold", 0, 0, 0, "Needs decompression."),
]

def run():
    url = os.environ["DATABASE_URL"]
    with psycopg.connect(url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            # seed only if table is empty
            cur.execute("SELECT COUNT(*) AS c FROM dogs;")
            if cur.fetchone()["c"] == 0:
                cur.executemany(
                    "INSERT INTO dogs (name, age, size, status, kid_friendly, cat_friendly, dog_friendly, notes) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    SEED,
                )
        conn.commit()
    print("Postgres ready (table ensured, seeds applied if empty).")

if __name__ == "__main__":
    run()


