from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session
from app.database import get_session
from app.models import (
    User,
    FinancialRecordType,
    FinancialRecordCreate,
    FinancialRecordUpdate,
    FinancialRecordRead,
)
from app.security import require_admin, require_analyst
from app.crud.record import record as crud_record

router = APIRouter(prefix="/records", tags=["records"])


class PaginatedRecordsResponse(BaseModel):
    items: List[FinancialRecordRead]
    total: int
    skip: int
    limit: int


@router.post("", response_model=FinancialRecordRead, status_code=201, dependencies=[Depends(require_admin)])
def create_record(obj_in: FinancialRecordCreate, db: Session = Depends(get_session)):
    return crud_record.create(db, obj_in=obj_in)


@router.get("", response_model=PaginatedRecordsResponse)
def read_records(
    db: Session = Depends(get_session),
    user: User = Depends(require_analyst),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[FinancialRecordType] = Query(None, description="Filter by type (income/expense)"),
    start_date: Optional[datetime] = Query(None, description="Filter records from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter records until this date")
):
    items = crud_record.get_multi(
        db, skip=skip, limit=limit, 
        category=category, type=type, 
        start_date=start_date, end_date=end_date
    )
    total = crud_record.count(
        db, category=category, type=type,
        start_date=start_date, end_date=end_date
    )
    return PaginatedRecordsResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{record_id}", response_model=FinancialRecordRead)
def read_record(
    record_id: int,
    db: Session = Depends(get_session),
    user: User = Depends(require_analyst)
):
    db_obj = crud_record.get(db, record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_obj


@router.patch("/{record_id}", response_model=FinancialRecordRead, dependencies=[Depends(require_admin)])
def update_record(record_id: int, obj_in: FinancialRecordUpdate, db: Session = Depends(get_session)):
    db_obj = crud_record.get(db, record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Record not found")
    return crud_record.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{record_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_record(record_id: int, db: Session = Depends(get_session)):
    db_obj = crud_record.get(db, record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Record not found")
    crud_record.remove(db, id=record_id)
    return None
