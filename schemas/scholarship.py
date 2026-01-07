# schemas/scholarship.py
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List


class ScholarshipBase(BaseModel):
    name: str
    description: str
    amount: Decimal
    deadline: date
    eligibility: Optional[str] = None
    application_url: Optional[str] = None
    eligibility_criteria: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class ScholarshipCreate(ScholarshipBase):
    pass


class ScholarshipUpdate(ScholarshipBase):
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    deadline: Optional[date] = None


class ScholarshipRead(ScholarshipBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
