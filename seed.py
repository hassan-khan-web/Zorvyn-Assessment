import random
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel
from app.database import engine
from app.models.user import User, UserRole, UserCreate
from app.models.record import FinancialRecord, FinancialRecordType, FinancialRecordCreate
from app.crud.user import user as crud_user
from app.crud.record import record as crud_record

def seed_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        admin_in = UserCreate(email="admin@example.com", role=UserRole.ADMIN)
        analyst_in = UserCreate(email="analyst@example.com", role=UserRole.ANALYST)
        viewer_in = UserCreate(email="viewer@example.com", role=UserRole.VIEWER)
        inactive_in = UserCreate(email="inactive@example.com", is_active=False)
        
        crud_user.create(session, obj_in=admin_in)
        crud_user.create(session, obj_in=analyst_in)
        crud_user.create(session, obj_in=viewer_in)
        crud_user.create(session, obj_in=inactive_in)
        
        # Get admin for ID
        admin = crud_user.get_by_email(session, "admin@example.com")
        
        categories = ["Rent", "Groceries", "Salary", "Investment", "Travel", "Subscriptions"]
        types = [FinancialRecordType.INCOME, FinancialRecordType.EXPENSE]
        
        for _ in range(50):
            record_in = FinancialRecordCreate(
                amount=round(random.uniform(10, 5000), 2),
                type=random.choice(types),
                category=random.choice(categories),
                date=datetime.now() - timedelta(days=random.randint(0, 90)),
                description=f"Automated seed entry",
                user_id=admin.id
            )
            crud_record.create(session, obj_in=record_in)
        
        print("Database seeded successfully using the CRUD layer.")

if __name__ == "__main__":
    seed_db()
