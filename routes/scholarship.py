# routes/scholarship.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal
from sqlalchemy import or_


from database import get_db
from models import scholarship
from schemas.scholarship import ScholarshipCreate, ScholarshipRead, ScholarshipUpdate

router = APIRouter(
    prefix="/scholarships",
    tags=["scholarships"],
)


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def create_scholarships_bulk(
    scholarships: List[ScholarshipCreate], db: Session = Depends(get_db)
):

    created_scholarships = []
    skipped_scholarships = []

    for scholarship_data in scholarships:
        existing_scholarship = (
            db.query(scholarship.Scholarship)
            .filter(scholarship.Scholarship.name == scholarship_data.name)
            .first()
        )

        if existing_scholarship:
            skipped_scholarships.append(
                {"name": scholarship_data.name, "reason": "Duplicate name"}
            )
            continue

        try:
            db_scholarship = scholarship.Scholarship(**scholarship_data.dict())
            db.add(db_scholarship)
            created_scholarships.append(db_scholarship)

        except Exception as e:
            skipped_scholarships.append(
                {"name": scholarship_data.name, "reason": str(e)}
            )
            continue

    if created_scholarships:
        try:
            db.commit()
            for db_scholarship in created_scholarships:
                db.refresh(db_scholarship)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Error committing scholarships: {str(e)}",
            )
    if skipped_scholarships:
        print(f"Skipped Scholarships: {skipped_scholarships}")

    return {
        "summary": {
            "created": len(created_scholarships),
            "skipped": len(skipped_scholarships),
        },
        "created_scholarships": created_scholarships,
        "skipped_scholarships": skipped_scholarships,
    }


@router.post("/", response_model=ScholarshipRead, status_code=status.HTTP_201_CREATED)
def create_scholarship(
    scholarship_in: ScholarshipCreate, db: Session = Depends(get_db)
):
    db_scholarship = scholarship.Scholarship(**scholarship_in.dict())
    db.add(db_scholarship)
    db.commit()
    db.refresh(db_scholarship)
    return db_scholarship


@router.get("/", response_model=List[ScholarshipRead])
def read_scholarships(
    skip: int = 0,
    limit: int = 100,
    deadline_before: Optional[date] = None,
    deadline_after: Optional[date] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(scholarship.Scholarship)

    if deadline_before:
        query = query.filter(scholarship.Scholarship.deadline <= deadline_before)
    if deadline_after:
        query = query.filter(scholarship.Scholarship.deadline >= deadline_after)
    if min_amount:
        query = query.filter(scholarship.Scholarship.amount >= min_amount)
    if max_amount:
        query = query.filter(scholarship.Scholarship.amount <= max_amount)
    if search:
        query = query.filter(
            or_(
                scholarship.Scholarship.name.ilike(f"%{search}%"),
                scholarship.Scholarship.description.ilike(f"%{search}%"),
                scholarship.Scholarship.tags.any(search),
            )
        )

    return query.offset(skip).limit(limit).all()


@router.get("/{scholarship_id}", response_model=ScholarshipRead)
def read_scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    db_scholarship = (
        db.query(scholarship.Scholarship)
        .filter(scholarship.Scholarship.id == scholarship_id)
        .first()
    )
    if db_scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return db_scholarship


@router.put("/{scholarship_id}", response_model=ScholarshipRead)
def update_scholarship(
    scholarship_id: int,
    scholarship_in: ScholarshipUpdate,
    db: Session = Depends(get_db),
):
    db_scholarship = (
        db.query(scholarship.Scholarship)
        .filter(scholarship.Scholarship.id == scholarship_id)
        .first()
    )
    if db_scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")

    for key, value in scholarship_in.dict(exclude_unset=True).items():
        setattr(db_scholarship, key, value)

    db.commit()
    db.refresh(db_scholarship)
    return db_scholarship


@router.delete("/{scholarship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    db_scholarship = (
        db.query(scholarship.Scholarship)
        .filter(scholarship.Scholarship.id == scholarship_id)
        .first()
    )
    if db_scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")

    db.delete(db_scholarship)
    db.commit()
    return None
