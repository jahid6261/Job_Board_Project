from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.users.models import EmployerRequestStatus
from typing import Literal

class EmployerRequestAdminResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    first_name: str
    last_name: str
    email: str
    number: str | None
    address: str | None
    reason: str | None
    status: EmployerRequestStatus
    created_at: datetime


class EmployerRequestActionSchema(BaseModel):
    status: Literal["approve", "reject"]    

class EmployerRequestCreateSchema(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=500,
    )    
class EmployerRequestResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    reason: str | None
    status: EmployerRequestStatus
    created_at: datetime
    updated_at: datetime | None    