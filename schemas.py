from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field

# --- Patient ---
class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    national_id: str = Field(min_length=3, max_length=20)
    date_of_birth: date | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None

class PatientOut(PatientBase):
    id: int
    class Config:
        from_attributes = True

# --- Visit ---
class VisitBase(BaseModel):
    complaint: str | None = None
    diagnosis: str | None = None
    notes: str | None = None

class VisitCreate(VisitBase):
    visit_time: datetime | None = None

class VisitOut(VisitBase):
    id: int
    patient_id: int
    visit_time: datetime
    class Config:
        from_attributes = True

# --- Medication ---
class MedicationBase(BaseModel):
    name: str
    dosage: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    instructions: str | None = None

class MedicationCreate(MedicationBase):
    pass

class MedicationOut(MedicationBase):
    id: int
    patient_id: int
    class Config:
        from_attributes = True
