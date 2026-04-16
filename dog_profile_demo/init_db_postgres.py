import os
from dotenv import load_dotenv

from app import create_app
from models import db

# Load environment variables
load_dotenv()


def init_postgres_database():
    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")

    app = create_app()

    with app.app_context():
        db.create_all()
        print("PostgreSQL database initialized successfully.")


if __name__ == "__main__":
    init_postgres_database()

