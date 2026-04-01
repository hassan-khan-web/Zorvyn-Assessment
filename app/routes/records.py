from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.models import User, FinancialRecord, FinancialRecordType, FinancialRecordCreate
from app.security import require_admin, require_analyst
from app.crud.record import record as crud_record

router = APIRouter(prefix="/records", tags=["records"])

@router.post("", response_model=FinancialRecord, dependencies=[Depends(require_admin)])
def create_record(obj_in: FinancialRecordCreate, db: Session = Depends(get_session)):
    return crud_record.create(db, obj_in=obj_in)

@router.get("", response_model=List[FinancialRecord])
def read_records(
    db: Session = Depends(get_session),
    user: User = Depends(require_analyst),
    category: Optional[str] = None,
    type: Optional[FinancialRecordType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    return crud_record.get_multi(db, category=category, type=type, start_date=start_date, end_date=end_date)

@router.get("/{record_id}", response_model=FinancialRecord)
def read_record(
    record_id: int,
    db: Session = Depends(get_session),
    user: User = Depends(require_analyst)
):
    db_obj = crud_record.get(db, record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_obj

@router.put("/{record_id}", response_model=FinancialRecord, dependencies=[Depends(require_admin)])
def update_record(record_id: int, obj_in: FinancialRecord, db: Session = Depends(get_session)):
    db_obj = crud_record.get(db, record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Record not found")
    return crud_record.update(db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{record_id}", dependencies=[Depends(require_admin)])
def delete_record(record_id: int, db: Session = Depends(get_session)):
    db_obj = crud_record.get(db, record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Record not found")
    crud_record.remove(db, id=record_id)
    return {"status": "success"}
