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
        return db.exec(statement).all()

    def create(self, db: Session, obj_in: FinancialRecordCreate) -> FinancialRecord:
        db_obj = FinancialRecord.model_validate(obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: FinancialRecord, obj_in: FinancialRecord) -> FinancialRecord:
        record_data = obj_in.model_dump(exclude_unset=True)
        for field in record_data:
            if field != "id":
                setattr(db_obj, field, record_data[field])
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
        income_stmt = select(func.sum(FinancialRecord.amount)).where(FinancialRecord.type == FinancialRecordType.INCOME)
        expense_stmt = select(func.sum(FinancialRecord.amount)).where(FinancialRecord.type == FinancialRecordType.EXPENSE)
        
        total_income = db.exec(income_stmt).one() or 0.0
        total_expense = db.exec(expense_stmt).one() or 0.0
        
        category_stmt = select(FinancialRecord.category, func.sum(FinancialRecord.amount)).group_by(FinancialRecord.category)
        category_totals = {cat: float(amt) for cat, amt in db.exec(category_stmt).all()}
        
        recent = db.exec(select(FinancialRecord).order_by(FinancialRecord.date.desc()).limit(5)).all()
        
        return {
            "total_income": total_income,
            "total_expenses": total_expense,
            "net_balance": total_income - total_expense,
            "category_wise_totals": category_totals,
            "recent_activity": recent
        }

    def get_trends(self, db: Session):
        trends_stmt = select(
            func.strftime('%Y-%m', FinancialRecord.date).label("month"),
            func.sum(FinancialRecord.amount).label("total")
        ).group_by("month").order_by("month")
        results = db.exec(trends_stmt).all()
        return [{"month": r[0], "total": float(r[1])} for r in results]

record = CRUDRecord()
