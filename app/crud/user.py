from typing import List, Optional
from sqlmodel import Session, select
from app.models.user import User, UserCreate

class CRUDUser:
    def get(self, db: Session, user_id: int) -> Optional[User]:
        return db.get(User, user_id)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.exec(select(User).where(User.email == email)).first()

    def exists_by_email(self, db: Session, email: str) -> bool:
        return db.exec(select(User).where(User.email == email)).first() is not None

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.exec(select(User).offset(skip).limit(limit)).all()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        db_obj = User.model_validate(obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "id":
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> Optional[User]:
        obj = db.get(User, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

user = CRUDUser()
