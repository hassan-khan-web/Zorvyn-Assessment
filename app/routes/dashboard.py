from typing import List, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from app.database import get_session
from app.models import User, FinancialRecordRead
from app.security import require_viewer
from app.crud.record import record as crud_record


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class CategoryTotal(BaseModel):
    category: str
    income: float
    expense: float
    net: float


class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    category_breakdown: List[CategoryTotal]
    recent_activity: List[FinancialRecordRead]


class TrendItem(BaseModel):
    month: str
    income: float
    expense: float
    net: float


class TrendsResponse(BaseModel):
    monthly_trends: List[TrendItem]


@router.get("/summary", response_model=SummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_session),
    user: User = Depends(require_viewer)
):
    return crud_record.get_summary(db)


@router.get("/trends", response_model=TrendsResponse)
def get_trends(
    db: Session = Depends(get_session),
    user: User = Depends(require_viewer)
):
    return crud_record.get_trends(db)
