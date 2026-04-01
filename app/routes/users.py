from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models import User, UserCreate
from app.security import require_admin
from app.crud.user import user as crud_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=User, dependencies=[Depends(require_admin)])
def create_user(obj_in: UserCreate, db: Session = Depends(get_session)):
    return crud_user.create(db, obj_in=obj_in)

@router.get("", response_model=List[User], dependencies=[Depends(require_admin)])
def read_users(db: Session = Depends(get_session)):
    return crud_user.get_multi(db)

@router.put("/{user_id}", response_model=User, dependencies=[Depends(require_admin)])
def update_user(user_id: int, obj_in: User, db: Session = Depends(get_session)):
    db_obj = crud_user.get(db, user_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_user.update(db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(user_id: int, db: Session = Depends(get_session)):
    db_obj = crud_user.get(db, user_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="User not found")
    crud_user.remove(db, id=user_id)
    return {"status": "success"}
