from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from . import models, schemas

# --- Patients ---
def create_patient(db: Session, data: schemas.PatientCreate) -> models.Patient:
    patient = models.Patient(**data.model_dict())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def get_patient(db: Session, patient_id: int):
    return db.get(models.Patient, patient_id)

def get_patient_by_national_id(db: Session, national_id: str):
    return db.execute(
        select(models.Patient).where(models.Patient.national_id == national_id)
    ).scalar_one_or_none()

def search_patients(db: Session, q: str | None, skip: int = 0, limit: int = 50):
    stmt = select(models.Patient).order_by(models.Patient.id.desc())
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                models.Patient.first_name.ilike(like),
                models.Patient.last_name.ilike(like),
                models.Patient.national_id.ilike(like),
                models.Patient.phone.ilike(like),
                models.Patient.email.ilike(like),
            )
        )
    return db.execute(stmt.offset(skip).limit(limit)).scalars().all()

def update_patient(db: Session, patient: models.Patient, data: schemas.PatientUpdate):
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(patient, k, v)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(db: Session, patient: models.Patient):
    db.delete(patient)
    db.commit()

# --- Visits ---
def create_visit(db: Session, patient_id: int, data: schemas.VisitCreate):
    visit_dict = data.model_dump()
    visit = models.Visit(patient_id=patient_id, **visit_dict)
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit

def list_visits(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    stmt = (select(models.Visit)
            .where(models.Visit.patient_id == patient_id)
            .order_by(models.Visit.visit_time.desc())
            .offset(skip).limit(limit))
    return db.execute(stmt).scalars().all()

# --- Medications ---
def create_medication(db: Session, patient_id: int, data: schemas.MedicationCreate):
    med = models.Medication(patient_id=patient_id, **data.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return med

def list_medications(db: Session, patient_id: int):
    stmt = select(models.Medication).where(models.Medication.patient_id == patient_id)
    return db.execute(stmt).scalars().all()
