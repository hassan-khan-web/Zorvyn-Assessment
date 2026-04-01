from enum import Enum
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

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
