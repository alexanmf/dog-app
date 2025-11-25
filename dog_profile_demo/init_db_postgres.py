import os
import sys

SCHEMA_FILE = "schema_postgres.sql"

def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set. Aborting.", file=sys.stderr)
        sys.exit(1)

    import psycopg2
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur, open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            sql = f.read()
            for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
                cur.execute(stmt)
        conn.commit()

        # Seed (same dogs, with booleans)
        dogs = [
            ("Buddy", 2, "Medium", "Intake", True, False, True, "Sweet and energetic. Microchip pending."),
            ("Molly", 7, "Small", "Fostered", True, True, True, "On thyroid meds. Great with kids."),
            ("Zeus", 4, "Large", "Hold", False, False, False, "Needs decompression. No cats."),
        ]
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO dogs
                (name, age, size, status, kid_friendly, cat_friendly, dog_friendly, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                dogs,
            )
        conn.commit()
        print("Initialized PostgreSQL with sample data.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
