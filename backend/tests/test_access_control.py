import os

os.environ.setdefault("AUTH_REQUIRED", "true")
os.environ.setdefault("ALLOW_TEST_AUTH_HEADER", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_access_control.db")

from fastapi.testclient import TestClient

import app.routes.insights as insights_route
import app.routes.simulation_insights as simulation_insights_route
from app.db.database import SessionLocal
from app.db.models import Statement, Transaction
from app.main import app


def _create_statement(owner_id: str, filename: str = "test.csv") -> int:
    db = SessionLocal()
    try:
        statement = Statement(owner_id=owner_id, filename=filename)
        db.add(statement)
        db.commit()
        db.refresh(statement)

        db.add(
            Transaction(
                statement_id=statement.id,
                date="2026-03-01",
                merchant="Test Merchant",
                description="Test debit",
                amount=123.45,
                direction="debit",
                category="groceries",
            )
        )
        db.commit()
        return statement.id
    finally:
        db.close()


def _delete_statement(statement_id: int) -> None:
    db = SessionLocal()
    try:
        statement = db.query(Statement).filter(Statement.id == statement_id).first()
        if statement:
            db.delete(statement)
            db.commit()
    finally:
        db.close()


def test_requires_auth_header_for_private_endpoints():
    os.environ["ENVIRONMENT"] = "production"
    statement_id = _create_statement("owner-auth-required")
    try:
        client = TestClient(app)
        response = client.get(f"/summary/{statement_id}")
        assert response.status_code == 401
    finally:
        os.environ["ENVIRONMENT"] = "development"
        _delete_statement(statement_id)


def test_owner_can_access_and_non_owner_is_blocked(monkeypatch):
    monkeypatch.setattr(insights_route, "generate_spending_insights", lambda _summary: "ok")
    monkeypatch.setattr(
        simulation_insights_route,
        "generate_simulation_insight",
        lambda **_kwargs: "ok",
    )

    statement_id = _create_statement("owner-a")
    try:
        owner_client = TestClient(app)
        other_client = TestClient(app)
        owner_headers = {"X-Test-User-Id": "owner-a"}
        other_headers = {"X-Test-User-Id": "owner-b"}

        owner_checks = [
            ("GET", f"/statements/{statement_id}", None),
            ("GET", f"/summary/{statement_id}", None),
            ("GET", f"/insights/{statement_id}", None),
            ("POST", f"/simulate/{statement_id}", {"category_reductions": {"groceries": 20}}),
            (
                "POST",
                f"/simulation-insights/{statement_id}",
                {"strategy": {"category_reductions": {"groceries": 20}}, "goals": []},
            ),
        ]

        for method, path, payload in owner_checks:
            if method == "GET":
                response = owner_client.get(path, headers=owner_headers)
            else:
                response = owner_client.post(path, json=payload, headers=owner_headers)
            assert response.status_code == 200

        for method, path, payload in owner_checks:
            if method == "GET":
                response = other_client.get(path, headers=other_headers)
            else:
                response = other_client.post(path, json=payload, headers=other_headers)
            assert response.status_code == 404
    finally:
        _delete_statement(statement_id)


def test_upload_persists_owner_id():
    client = TestClient(app)
    headers = {"X-Test-User-Id": "owner-upload"}
    csv_content = b"Date,Description,Amount\n2026-03-01,Store Purchase,-24.50\n"

    response = client.post(
        "/upload/csv",
        files={"file": ("statement.csv", csv_content, "text/csv")},
        headers=headers,
    )
    assert response.status_code == 200

    statement_id = response.json()["statement_id"]
    try:
        db = SessionLocal()
        try:
            statement = db.query(Statement).filter(Statement.id == statement_id).first()
            assert statement is not None
            assert statement.owner_id == "owner-upload"
        finally:
            db.close()
    finally:
        _delete_statement(statement_id)
