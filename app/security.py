from fastapi import HTTPException, Depends, Header
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, UserRole

def get_current_user(email: str = Header(...), session: Session = Depends(get_session)) -> User:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Operation not permitted for role: {user.role.value}"
            )
        return user

def require_admin(user: User = Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def require_analyst(user: User = Depends(get_current_user)):
    if user.role not in [UserRole.ADMIN, UserRole.ANALYST]:
        raise HTTPException(status_code=403, detail="Analyst access required")
    return user

def require_viewer(user: User = Depends(get_current_user)):
    return user
