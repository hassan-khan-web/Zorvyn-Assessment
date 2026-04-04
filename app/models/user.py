from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.record import FinancialRecord

class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    role: UserRole = Field(default=UserRole.VIEWER)
    is_active: bool = Field(default=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    records: List["FinancialRecord"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    email: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserRead(SQLModel):
    id: int
    email: str
    role: UserRole
    is_active: bool
