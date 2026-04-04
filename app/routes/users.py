from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.models import User, UserCreate, UserUpdate, UserRead
from app.security import require_admin
from app.crud.user import user as crud_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201, dependencies=[Depends(require_admin)])
def create_user(obj_in: UserCreate, db: Session = Depends(get_session)):
    if crud_user.exists_by_email(db, obj_in.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud_user.create(db, obj_in=obj_in)


@router.get("", response_model=List[UserRead], dependencies=[Depends(require_admin)])
def read_users(
    db: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return")
):
    return crud_user.get_multi(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_admin)])
def read_user(user_id: int, db: Session = Depends(get_session)):
    db_obj = crud_user.get(db, user_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return db_obj


@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(require_admin)])
def update_user(user_id: int, obj_in: UserUpdate, db: Session = Depends(get_session)):
    db_obj = crud_user.get(db, user_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if obj_in.email and obj_in.email != db_obj.email:
        if crud_user.exists_by_email(db, obj_in.email):
            raise HTTPException(status_code=409, detail="Email already registered")
    return crud_user.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_user(user_id: int, db: Session = Depends(get_session)):
    db_obj = crud_user.get(db, user_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="User not found")
    crud_user.remove(db, id=user_id)
    return None
