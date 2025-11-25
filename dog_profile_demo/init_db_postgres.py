import os, sys
SCHEMA_FILE = "schema_postgres.sql"

def main():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set", file=sys.stderr); sys.exit(1)

    import psycopg
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur, open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            sql = f.read()
            for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
                cur.execute(stmt)
        conn.commit()

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

if __name__ == "__main__":
    main()

