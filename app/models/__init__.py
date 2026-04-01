from app.models.user import User, UserRole, UserCreate
from app.models.record import FinancialRecord, FinancialRecordType, FinancialRecordBase, FinancialRecordCreate

# Handle typing for circular relationships
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.record import FinancialRecord
    from app.models.user import User
