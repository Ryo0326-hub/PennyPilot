import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_owner_column() -> None:
    inspector = inspect(engine)
    if "statements" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("statements")}
    if "owner_id" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE statements ADD COLUMN owner_id VARCHAR(255) "
                    "NOT NULL DEFAULT 'legacy-local-user'"
                )
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_statements_owner_id "
                    "ON statements(owner_id)"
                )
            )
    else:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE statements SET owner_id = 'legacy-local-user' "
                    "WHERE owner_id IS NULL OR owner_id = ''"
                )
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()