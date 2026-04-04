import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.database import get_session
from main import app
from app.models.user import User, UserRole


sqlite_url = "sqlite:///test.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


@pytest.fixture(name="session", scope="module", autouse=True)
def session_fixture():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        admin = User(email="admin@test.com", role=UserRole.ADMIN)
        analyst = User(email="analyst@test.com", role=UserRole.ANALYST)
        viewer = User(email="viewer@test.com", role=UserRole.VIEWER)
        inactive = User(email="inactive@test.com", role=UserRole.VIEWER, is_active=False)
        session.add_all([admin, analyst, viewer, inactive])
        session.commit()
        yield session
    SQLModel.metadata.drop_all(engine)


# ==================== Authentication Tests ====================

def test_invalid_auth_returns_401():
    response = client.get("/records", headers={"email": "nonexistent@test.com"})
    assert response.status_code == 401
    assert "Invalid authentication" in response.json()["detail"]


def test_inactive_user_returns_403():
    response = client.get("/records", headers={"email": "inactive@test.com"})
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


def test_missing_auth_header_returns_422():
    response = client.get("/records")
    assert response.status_code == 422


# ==================== User Management Tests ====================

def test_admin_can_create_user():
    response = client.post(
        "/users",
        headers={"email": "admin@test.com"},
        json={"email": "newuser@test.com", "role": "viewer"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@test.com"
    assert response.json()["role"] == "viewer"


def test_duplicate_email_returns_409():
    response = client.post(
        "/users",
        headers={"email": "admin@test.com"},
        json={"email": "admin@test.com", "role": "viewer"}
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_viewer_cannot_create_user():
    response = client.post(
        "/users",
        headers={"email": "viewer@test.com"},
        json={"email": "another@test.com", "role": "viewer"}
    )
    assert response.status_code == 403


def test_admin_can_list_users():
    response = client.get("/users", headers={"email": "admin@test.com"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 4


def test_admin_can_update_user():
    response = client.patch(
        "/users/5",
        headers={"email": "admin@test.com"},
        json={"role": "analyst"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "analyst"


def test_update_nonexistent_user_returns_404():
    response = client.patch(
        "/users/9999",
        headers={"email": "admin@test.com"},
        json={"role": "admin"}
    )
    assert response.status_code == 404


def test_admin_can_delete_user():
    create_resp = client.post(
        "/users",
        headers={"email": "admin@test.com"},
        json={"email": "todelete@test.com", "role": "viewer"}
    )
    user_id = create_resp.json()["id"]
    
    response = client.delete(f"/users/{user_id}", headers={"email": "admin@test.com"})
    assert response.status_code == 204


# ==================== Financial Record Tests ====================

def test_admin_can_create_record():
    response = client.post(
        "/records",
        headers={"email": "admin@test.com"},
        json={
            "amount": 1000.50,
            "type": "income",
            "category": "Salary",
            "description": "Monthly salary",
            "user_id": 1
        }
    )
    assert response.status_code == 201
    assert response.json()["amount"] == 1000.50
    assert response.json()["type"] == "income"


def test_viewer_cannot_create_record():
    response = client.post(
        "/records",
        headers={"email": "viewer@test.com"},
        json={"amount": 50.0, "type": "expense", "category": "Food", "user_id": 3}
    )
    assert response.status_code == 403


def test_negative_amount_validation():
    response = client.post(
        "/records",
        headers={"email": "admin@test.com"},
        json={"amount": -10.0, "type": "expense", "category": "Error", "user_id": 1}
    )
    assert response.status_code == 422


def test_invalid_record_type_validation():
    response = client.post(
        "/records",
        headers={"email": "admin@test.com"},
        json={"amount": 100.0, "type": "invalid_type", "category": "Test", "user_id": 1}
    )
    assert response.status_code == 422


def test_analyst_can_view_records():
    response = client.get("/records", headers={"email": "analyst@test.com"})
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert len(response.json()["items"]) >= 1


def test_viewer_cannot_view_records():
    response = client.get("/records", headers={"email": "viewer@test.com"})
    assert response.status_code == 403


def test_records_pagination():
    for i in range(5):
        client.post(
            "/records",
            headers={"email": "admin@test.com"},
            json={"amount": 10.0 + i, "type": "expense", "category": "Test", "user_id": 1}
        )
    
    response = client.get(
        "/records?skip=0&limit=3",
        headers={"email": "analyst@test.com"}
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 3
    assert response.json()["total"] >= 5


def test_records_filter_by_category():
    client.post(
        "/records",
        headers={"email": "admin@test.com"},
        json={"amount": 500.0, "type": "expense", "category": "UniqueCategory", "user_id": 1}
    )
    
    response = client.get(
        "/records?category=UniqueCategory",
        headers={"email": "analyst@test.com"}
    )
    assert response.status_code == 200
    assert all(r["category"] == "UniqueCategory" for r in response.json()["items"])


def test_records_filter_by_type():
    response = client.get(
        "/records?type=income",
        headers={"email": "analyst@test.com"}
    )
    assert response.status_code == 200
    assert all(r["type"] == "income" for r in response.json()["items"])


def test_admin_can_update_record():
    create_resp = client.post(
        "/records",
        headers={"email": "admin@test.com"},
        json={"amount": 100.0, "type": "expense", "category": "Original", "user_id": 1}
    )
    record_id = create_resp.json()["id"]
    
    response = client.patch(
        f"/records/{record_id}",
        headers={"email": "admin@test.com"},
        json={"category": "Updated", "amount": 150.0}
    )
    assert response.status_code == 200
    assert response.json()["category"] == "Updated"
    assert response.json()["amount"] == 150.0


def test_analyst_cannot_update_record():
    response = client.patch(
        "/records/1",
        headers={"email": "analyst@test.com"},
        json={"category": "Hacked"}
    )
    assert response.status_code == 403


def test_admin_can_delete_record():
    create_resp = client.post(
        "/records",
        headers={"email": "admin@test.com"},
        json={"amount": 10.0, "type": "expense", "category": "ToDelete", "user_id": 1}
    )
    record_id = create_resp.json()["id"]
    
    response = client.delete(f"/records/{record_id}", headers={"email": "admin@test.com"})
    assert response.status_code == 204
    
    get_resp = client.get(f"/records/{record_id}", headers={"email": "analyst@test.com"})
    assert get_resp.status_code == 404


# ==================== Dashboard Tests ====================

def test_viewer_can_access_dashboard_summary():
    response = client.get("/dashboard/summary", headers={"email": "viewer@test.com"})
    assert response.status_code == 200
    data = response.json()
    assert "total_income" in data
    assert "total_expenses" in data
    assert "net_balance" in data
    assert "category_breakdown" in data
    assert "recent_activity" in data


def test_dashboard_summary_calculations():
    response = client.get("/dashboard/summary", headers={"email": "viewer@test.com"})
    data = response.json()
    assert data["net_balance"] == data["total_income"] - data["total_expenses"]


def test_viewer_can_access_trends():
    response = client.get("/dashboard/trends", headers={"email": "viewer@test.com"})
    assert response.status_code == 200
    data = response.json()
    assert "monthly_trends" in data
    assert isinstance(data["monthly_trends"], list)


def test_trends_contain_income_expense_breakdown():
    response = client.get("/dashboard/trends", headers={"email": "viewer@test.com"})
    data = response.json()
    if len(data["monthly_trends"]) > 0:
        trend = data["monthly_trends"][0]
        assert "income" in trend
        assert "expense" in trend
        assert "net" in trend
        assert trend["net"] == trend["income"] - trend["expense"]


def test_category_breakdown_structure():
    response = client.get("/dashboard/summary", headers={"email": "viewer@test.com"})
    data = response.json()
    if len(data["category_breakdown"]) > 0:
        cat = data["category_breakdown"][0]
        assert "category" in cat
        assert "income" in cat
        assert "expense" in cat
        assert "net" in cat
