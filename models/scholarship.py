# models/scholarship.py
from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from database import Base


class Scholarship(Base):
    __tablename__ = "scholarships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    deadline = Column(Date, nullable=False)
    eligibility = Column(Text)
    application_url = Column(String(500))
    eligibility_criteria = Column(JSONB)
    tags = Column(ARRAY(String(50)))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
