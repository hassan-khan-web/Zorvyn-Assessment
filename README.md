# Finance Dashboard Backend

A professional, role-based backend for financial management systems. Built with **FastAPI**, **SQLModel**, and **SQLite**.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed the Database
```bash
python seed.py
```

### 3. Run the Server
```bash
uvicorn main:app --reload
```

## 🔐 Access Control Model

The system uses header-based mock authentication. Include the `email` header in your requests.

| Role | Mock Email | Permissions |
| :--- | :--- | :--- |
| **Admin** | `admin@example.com` | Full CRUD for Users and Financial Records. |
| **Analyst** | `analyst@example.com` | Read-only access to Records and Summaries. |
| **Viewer** | `viewer@example.com` | Access to Dashboard Summaries only. |

## 📊 API Endpoints

### User Management (Admin Only)
- `POST /users`: Create new users.
- `GET /users`: List all users.
- `PUT /users/{id}`: Update user role/status.
- `DELETE /users/{id}`: Remove a user.

### Financial Records
- `POST /records`: Create entries (Admin).
- `GET /records`: List filtered records (Admin, Analyst).
- `GET /records/{id}`: Detailed record view (Admin, Analyst).
- `PUT /records/{id}`: Update entries (Admin).
- `DELETE /records/{id}`: Delete entries (Admin).

### Dashboard Analytics
- `GET /dashboard/summary`: Aggregate stats (Income, Expense, Balance).
- `GET /dashboard/trends`: Time-series monthly aggregation.

## 🏗️ Architecture & Tradeoffs

- **SQLModel**: Chosen for its dual role as a Pydantic model and SQLAlchemy ORM, ensuring perfect type alignment between the DB and API layers.
- **SQLite**: Used for local persistence to simplify deployment and review.
- **Mock Header Auth**: Used to focus on RBAC logic rather than JWT/OAuth2 boilerplate.
- **Aggregations**: Summary calculations are performed using SQL `func` calls for efficiency.

## 🧪 Testing
Run the automated test suite to verify business rules:
```bash
pytest test_api.py
```
