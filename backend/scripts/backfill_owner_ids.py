from app.db.database import SessionLocal
from app.db.models import Statement


def main() -> None:
    db = SessionLocal()
    try:
        updated = (
            db.query(Statement)
            .filter((Statement.owner_id.is_(None)) | (Statement.owner_id == ""))
            .update({"owner_id": "legacy-local-user"}, synchronize_session=False)
        )
        db.commit()
        print(f"Backfilled owner_id for {updated} statement(s).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
