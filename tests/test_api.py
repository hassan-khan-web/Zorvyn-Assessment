import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from app.database import get_session
from main import app
from app.models.user import User, UserRole
from app.models.record import FinancialRecord, FinancialRecordType

sqlite_url = "sqlite:///test.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)

@pytest.fixture(name="session", scope="module", autouse=True)
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        admin = User(email="admin@test.com", role=UserRole.ADMIN)
        analyst = User(email="analyst@test.com", role=UserRole.ANALYST)
        viewer = User(email="viewer@test.com", role=UserRole.VIEWER)
        session.add_all([admin, analyst, viewer])
        session.commit()
        yield session
    SQLModel.metadata.drop_all(engine)

def test_admin_create_record():
    response = client.post(
        "/records",
        headers={"email": "admin@test.com"},
        json={
            "amount": 100.50,
            "type": "income",
            "category": "Salary",
            "description": "Test Income",
            "user_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 100.50

def test_viewer_cannot_create_record():
    response = client.post(
        "/records",
        headers={"email": "viewer@test.com"},
        json={"amount": 50.0, "type": "expense", "category": "Food", "user_id": 3}
    )
    assert response.status_code == 403

def test_analyst_can_view_records():
    response = client.get("/records", headers={"email": "analyst@test.com"})
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_dashboard_summary():
    response = client.get("/dashboard/summary", headers={"email": "viewer@test.com"})
    assert response.status_code == 200
    assert "total_income" in response.json()

def test_invalid_auth():
    response = client.get("/records", headers={"email": "nonexistent@test.com"})
    assert response.status_code == 401

def test_negative_amount_validation():
    response = client.post(
        "/records",
        headers={"email": "admin@test.com"},
        json={"amount": -10.0, "type": "expense", "category": "Error", "user_id": 1}
    )
    assert response.status_code == 422
