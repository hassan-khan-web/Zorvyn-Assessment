# Finance Dashboard Backend & Analytics System

A professional-grade, role-based finance management system built with **FastAPI**, **SQLModel**, and **SQLite**. This project demonstrates a clean, modular architecture with strict access control and real-time dashboard analytics.

---

## 🚀 Key Features

- **Advanced Role-Based Access Control (RBAC)**:
  - **Admin**: Full authority to manage users and financial records.
  - **Analyst**: Access to detailed records and visual insights.
  - **Viewer**: Read-only access to high-level dashboard summaries.
- **Enterprise Architecture**: Modular design featuring a dedicated **CRUD layer**, isolated models, and package-based routing.
- **Visual Analytics**: Real-time aggregation of income, expenses, net balance, and monthly trends.
- **Automated Reliability**: Comprehensive `pytest` suite ensuring 100% compliance with business rules and security guards.
- **Interactive Interface**: A premium, glassmorphism-styled dashboard to visualize backend data flow.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Async-ready, high performance)
- **Database**: SQLModel (SQLAlchemy 2.0 core + Pydantic validation)
- **Security**: Dependency-based role guards (Mock Header Authentication)
- **Environment**: Conda-based dependency management
- **Frontend**: Vanilla HTML5 / CSS3 (Glassmorphism) / JavaScript (Fetch API)

---

## 📂 Project Structure

```text
.
├── app/
│   ├── crud/          # Unified Database Operations (Decoupled Logic)
│   ├── database/      # Session & Engine Configuration
│   ├── models/        # Modular Pydantic & SQLModel Definitions
│   ├── routes/        # Modularized API Endpoints (Users, Records, Dashboard)
│   └── security.py    # RBAC & Mock Auth Guards
├── static/            # Frontend Assets (Served directly by FastAPI)
├── tests/             # Automated Integration & Unit Tests
├── main.py            # Application Entry Point
├── seed.py            # Automated Database Seeding Utility
└── environment.yml    # Conda Environment Configuration
```

---

## ⚙️ Setup & Installation

### 1. Environment Setup (Recommended)
This project uses **Conda** for isolation.
```bash
# Create and activate the environment
conda env create -f environment.yml
conda activate finance-dashboard
```

### 2. Database Initialization
Seed the database with mock users (Admin, Analyst, Viewer) and 50+ financial records:
```bash
python seed.py
```

### 3. Run the Application
```bash
uvicorn main:app --reload
```
Visit **[http://localhost:8000](http://localhost:8000)** to view the interactive dashboard.

---

## 🧪 Testing & Documentation

### Automated Tests
Run the full verification suite:
```bash
PYTHONPATH=. pytest tests/test_api.py
```

### API Documentation
FastAPI automatically generates interactive Swagger documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧠 Design Decisions & Assumptions

- **CRUD Layer**: We implemented a dedicated CRUD layer to decouple business logic from the API routes, making the system highly testable and reusable.
- **Mock Header Auth**: For the purpose of this assessment, authentication is handled via an `email` header to demonstrate RBAC logic without OAuth2 boilerplate.
- **Data Integrity**: Used SQLModel's validation (e.g., `ge=0` for amounts) to ensure data correctness at the entry point.
- **Pure Code Standard**: Zero comments were used in the source code; the implementation relies on descriptive naming and logical organization to speak for itself.
