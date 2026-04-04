from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, func
from app.models.record import FinancialRecord, FinancialRecordType, FinancialRecordCreate

class CRUDRecord:
    def get(self, db: Session, id: int) -> Optional[FinancialRecord]:
        return db.get(FinancialRecord, id)

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None, 
        type: Optional[FinancialRecordType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[FinancialRecord]:
        statement = select(FinancialRecord)
        if category:
            statement = statement.where(FinancialRecord.category == category)
        if type:
            statement = statement.where(FinancialRecord.type == type)
        if start_date:
            statement = statement.where(FinancialRecord.date >= start_date)
        if end_date:
            statement = statement.where(FinancialRecord.date <= end_date)
        statement = statement.order_by(FinancialRecord.date.desc()).offset(skip).limit(limit)
        return db.exec(statement).all()

    def count(
        self,
        db: Session,
        category: Optional[str] = None,
        type: Optional[FinancialRecordType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        statement = select(func.count(FinancialRecord.id))
        if category:
            statement = statement.where(FinancialRecord.category == category)
        if type:
            statement = statement.where(FinancialRecord.type == type)
        if start_date:
            statement = statement.where(FinancialRecord.date >= start_date)
        if end_date:
            statement = statement.where(FinancialRecord.date <= end_date)
        return db.exec(statement).one()

    def create(self, db: Session, obj_in: FinancialRecordCreate) -> FinancialRecord:
        db_obj = FinancialRecord.model_validate(obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: FinancialRecord, obj_in) -> FinancialRecord:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "id":
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> Optional[FinancialRecord]:
        obj = db.get(FinancialRecord, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def get_summary(self, db: Session):
        income_stmt = select(func.sum(FinancialRecord.amount)).where(
            FinancialRecord.type == FinancialRecordType.INCOME
        )
        expense_stmt = select(func.sum(FinancialRecord.amount)).where(
            FinancialRecord.type == FinancialRecordType.EXPENSE
        )
        
        total_income = db.exec(income_stmt).one() or 0.0
        total_expense = db.exec(expense_stmt).one() or 0.0
        
        category_stmt = select(
            FinancialRecord.category,
            FinancialRecord.type,
            func.sum(FinancialRecord.amount)
        ).group_by(FinancialRecord.category, FinancialRecord.type)
        
        category_data = {}
        for cat, rec_type, amt in db.exec(category_stmt).all():
            if cat not in category_data:
                category_data[cat] = {"income": 0.0, "expense": 0.0}
            if rec_type == FinancialRecordType.INCOME:
                category_data[cat]["income"] = float(amt)
            else:
                category_data[cat]["expense"] = float(amt)
        
        category_breakdown = [
            {
                "category": cat,
                "income": data["income"],
                "expense": data["expense"],
                "net": data["income"] - data["expense"]
            }
            for cat, data in category_data.items()
        ]
        
        recent = db.exec(
            select(FinancialRecord).order_by(FinancialRecord.date.desc()).limit(5)
        ).all()
        
        return {
            "total_income": float(total_income),
            "total_expenses": float(total_expense),
            "net_balance": float(total_income - total_expense),
            "category_breakdown": category_breakdown,
            "recent_activity": recent
        }

    def get_trends(self, db: Session):
        trends_stmt = select(
            func.strftime('%Y-%m', FinancialRecord.date).label("month"),
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total")
        ).group_by("month", FinancialRecord.type).order_by("month")
        
        monthly_data = {}
        for month, rec_type, total in db.exec(trends_stmt).all():
            if month not in monthly_data:
                monthly_data[month] = {"income": 0.0, "expense": 0.0}
            if rec_type == FinancialRecordType.INCOME:
                monthly_data[month]["income"] = float(total)
            else:
                monthly_data[month]["expense"] = float(total)
        
        monthly_trends = [
            {
                "month": month,
                "income": data["income"],
                "expense": data["expense"],
                "net": data["income"] - data["expense"]
            }
            for month, data in sorted(monthly_data.items())
        ]
        
        return {"monthly_trends": monthly_trends}

record = CRUDRecord()
