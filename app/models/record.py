from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.user import User

class FinancialRecordType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class FinancialRecordBase(SQLModel):
    amount: float = Field(ge=0)
    type: FinancialRecordType
    category: str
    date: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = None

class FinancialRecord(FinancialRecordBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="records")

class FinancialRecordCreate(FinancialRecordBase):
    user_id: int


class FinancialRecordUpdate(SQLModel):
    amount: float | None = Field(default=None, ge=0)
    type: FinancialRecordType | None = None
    category: str | None = None
    date: datetime | None = None
    description: str | None = None


class FinancialRecordRead(SQLModel):
    id: int
    amount: float
    type: FinancialRecordType
    category: str
    date: datetime
    description: str | None
    user_id: int
