from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.models import User
from app.security import require_viewer
from app.crud.record import record as crud_record

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_session),
    user: User = Depends(require_viewer)
):
    return crud_record.get_summary(db)

@router.get("/trends")
def get_trends(
    db: Session = Depends(get_session),
    user: User = Depends(require_viewer)
):
    return crud_record.get_trends(db)
