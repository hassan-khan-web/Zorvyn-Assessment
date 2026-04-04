# Finance Dashboard Backend & Analytics System

A professional-grade, role-based finance management system built with **FastAPI**, **SQLModel**, and **SQLite**. This project demonstrates a clean, modular architecture with strict access control and real-time dashboard analytics.

---

## 🚀 Key Features

- **Advanced Role-Based Access Control (RBAC)**:
  - **Admin**: Full authority to manage users and financial records
  - **Analyst**: Access to detailed records and visual insights
  - **Viewer**: Read-only access to dashboard summaries
- **Enterprise Architecture**: Modular design featuring a dedicated **CRUD layer**, isolated models, and package-based routing
- **Visual Analytics**: Real-time aggregation of income, expenses, net balance, category breakdown, and monthly trends
- **Paginated APIs**: Scalable record listing with filtering capabilities
- **Comprehensive Testing**: 27 automated tests ensuring business rules and security compliance
- **Interactive Interface**: Glassmorphism-styled dashboard to visualize backend data flow

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Async-ready, high performance) |
| **ORM** | SQLModel (SQLAlchemy 2.0 + Pydantic validation) |
| **Database** | SQLite (easily swappable to PostgreSQL) |
| **Security** | Dependency-based role guards |
| **Testing** | pytest with TestClient |
| **Docs** | Auto-generated OpenAPI (Swagger/ReDoc) |

---

## 📂 Project Structure

```text
.
├── app/
│   ├── crud/          # Database operations layer (decoupled from routes)
│   ├── database/      # Session & engine configuration
│   ├── models/        # Pydantic & SQLModel schemas
│   ├── routes/        # API endpoints (users, records, dashboard)
│   └── security.py    # RBAC guards & authentication
├── static/            # Frontend assets
├── tests/             # Automated test suite (27 tests)
├── main.py            # Application entry point
├── seed.py            # Database seeding utility
└── requirements.txt   # Python dependencies
```

---

## ⚙️ Setup & Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Seed the Database
```bash
python seed.py
```
This creates mock users (Admin, Analyst, Viewer) and 50 financial records.

### 3. Run the Application
```bash
uvicorn main:app --reload
```
Visit **http://localhost:8000** for the dashboard, or **/docs** for Swagger UI.

---

## 🔐 Role-Permission Matrix

| Action | Viewer | Analyst | Admin |
|--------|:------:|:-------:|:-----:|
| View dashboard summary | ✅ | ✅ | ✅ |
| View trends | ✅ | ✅ | ✅ |
| List records | ❌ | ✅ | ✅ |
| View single record | ❌ | ✅ | ✅ |
| Create record | ❌ | ❌ | ✅ |
| Update record | ❌ | ❌ | ✅ |
| Delete record | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

---

## 📡 API Reference

### Authentication
All endpoints require an `email` header for mock authentication:
```bash
curl -H "email: admin@example.com" http://localhost:8000/users
```

### Users (`/users`)

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `POST` | `/users` | Create user | Admin |
| `GET` | `/users` | List users (paginated) | Admin |
| `GET` | `/users/{id}` | Get user by ID | Admin |
| `PATCH` | `/users/{id}` | Update user | Admin |
| `DELETE` | `/users/{id}` | Delete user | Admin |

### Financial Records (`/records`)

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `POST` | `/records` | Create record | Admin |
| `GET` | `/records` | List records (paginated, filterable) | Analyst+ |
| `GET` | `/records/{id}` | Get record by ID | Analyst+ |
| `PATCH` | `/records/{id}` | Update record | Admin |
| `DELETE` | `/records/{id}` | Delete record | Admin |

**Query Parameters for `GET /records`:**
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Max results per page (default: 20, max: 100)
- `category` (string): Filter by category
- `type` (enum): Filter by `income` or `expense`
- `start_date` (datetime): Filter from date
- `end_date` (datetime): Filter until date

### Dashboard (`/dashboard`)

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `GET` | `/dashboard/summary` | Financial overview | All |
| `GET` | `/dashboard/trends` | Monthly income/expense trends | All |

**Summary Response:**
```json
{
  "total_income": 15000.00,
  "total_expenses": 8500.00,
  "net_balance": 6500.00,
  "category_breakdown": [
    {"category": "Salary", "income": 10000, "expense": 0, "net": 10000}
  ],
  "recent_activity": [...]
}
```

---

## 🧪 Testing

Run the full test suite:
```bash
PYTHONPATH=. pytest tests/test_api.py -v
```

**Test Coverage:**
- Authentication (3 tests): Invalid credentials, inactive users, missing headers
- User Management (7 tests): CRUD operations, duplicate email handling
- Financial Records (12 tests): CRUD, validation, pagination, filtering
- Dashboard (5 tests): Summary calculations, trends structure

---

## 🧠 Design Decisions & Assumptions

### Architecture Choices
1. **CRUD Layer Separation**: Business logic is decoupled from routes, making the system testable and reusable
2. **Pydantic Schemas**: Separate schemas for Create, Update, and Read operations ensure proper API contracts
3. **Dependency Injection**: FastAPI's `Depends()` system handles authentication and authorization cleanly

### Assumptions Made
1. **Mock Authentication**: Uses email header instead of JWT/OAuth2 to focus on RBAC logic
2. **Single Database**: SQLite for simplicity; can be swapped to PostgreSQL via connection string
3. **User-Record Relationship**: Records are linked to users via `user_id` for ownership tracking
4. **No Soft Delete**: Records are permanently deleted (could add `deleted_at` for production)

### Tradeoffs
| Decision | Benefit | Tradeoff |
|----------|---------|----------|
| SQLite | Zero setup, portable | Not suitable for concurrent production use |
| Email header auth | Simple demo of RBAC | Not secure for production |
| Sync endpoints | Simpler code | Could use async for higher throughput |

---

## 🔮 Potential Enhancements

- [ ] JWT token authentication
- [ ] Soft delete with `deleted_at` timestamp
- [ ] Search across record descriptions
- [ ] Export reports (CSV/PDF)
- [ ] Rate limiting middleware
- [ ] Docker containerization