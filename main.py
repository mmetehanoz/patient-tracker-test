from fastapi import FastAPI, Depends, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import schemas, models, crud

app = FastAPI(title="Patient Tracker", version="0.1.0")

# ilk kurulumda tabloları oluştur
Base.metadata.create_all(bind=engine)

# ---- Patients ----
@app.post("/patients", response_model=schemas.PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    existing = crud.get_patient_by_national_id(db, payload.national_id)
    if existing:
        raise HTTPException(400, detail="Bu T.C./Kimlik numarası zaten kayıtlı.")
    return crud.create_patient(db, payload)

@app.get("/patients/{patient_id}", response_model=schemas.PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(404, detail="Hasta bulunamadı.")
    return p

@app.get("/patients", response_model=list[schemas.PatientOut])
def list_patients(q: str | None = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.search_patients(db, q, skip, limit)

@app.patch("/patients/{patient_id}", response_model=schemas.PatientOut)
def update_patient(patient_id: int, payload: schemas.PatientUpdate, db: Session = Depends(get_db)):
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(404, detail="Hasta bulunamadı.")
    return crud.update_patient(db, p, payload)

@app.delete("/patients/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(404, detail="Hasta bulunamadı.")
    crud.delete_patient(db, p)
    return

# ---- Visits ----
@app.post("/patients/{patient_id}/visits", response_model=schemas.VisitOut, status_code=201)
def add_visit(patient_id: int, payload: schemas.VisitCreate, db: Session = Depends(get_db)):
    if not crud.get_patient(db, patient_id):
        raise HTTPException(404, detail="Hasta bulunamadı.")
    return crud.create_visit(db, patient_id, payload)

@app.get("/patients/{patient_id}/visits", response_model=list[schemas.VisitOut])
def list_visits(patient_id: int, db: Session = Depends(get_db)):
    if not crud.get_patient(db, patient_id):
        raise HTTPException(404, detail="Hasta bulunamadı.")
    return crud.list_visits(db, patient_id)

# ---- Medications ----
@app.post("/patients/{patient_id}/medications", response_model=schemas.MedicationOut, status_code=201)
def add_medication(patient_id: int, payload: schemas.MedicationCreate, db: Session = Depends(get_db)):
    if not crud.get_patient(db, patient_id):
        raise HTTPException(404, detail="Hasta bulunamadı.")
    return crud.create_medication(db, patient_id, payload)

@app.get("/patients/{patient_id}/medications", response_model=list[schemas.MedicationOut])
def list_medications(patient_id: int, db: Session = Depends(get_db)):
    if not crud.get_patient(db, patient_id):
        raise HTTPException(404, detail="Hasta bulunamadı.")
    return crud.list_medications(db, patient_id)

# ---- Basit CSV import (opsiyonel) ----
@app.post("/import/patients", response_model=list[schemas.PatientOut])
async def import_patients(file: UploadFile, db: Session = Depends(get_db)):
    """
    CSV bekler: first_name,last_name,national_id,date_of_birth,phone,email,address
    ISO tarih: YYYY-MM-DD
    """
    import csv, io, datetime
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    created = []
    for row in reader:
        dob = None
        if row.get("date_of_birth"):
            dob = datetime.date.fromisoformat(row["date_of_birth"])
        payload = schemas.PatientCreate(
            first_name=row.get("first_name",""),
            last_name=row.get("last_name",""),
            national_id=row.get("national_id",""),
            date_of_birth=dob,
            phone=row.get("phone") or None,
            email=row.get("email") or None,
            address=row.get("address") or None,
        )
        if crud.get_patient_by_national_id(db, payload.national_id):
            # var olanı atla
            continue
        created.append(crud.create_patient(db, payload))
    return created

@app.get("/")
def root():
    return {"ok": True, "service": "Patient Tracker API"}
