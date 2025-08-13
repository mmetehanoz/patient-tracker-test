from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .database import Base

class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(60), index=True)
    last_name: Mapped[str] = mapped_column(String(60), index=True)
    national_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # TC / pasaport vb.
    date_of_birth: Mapped[Date | None]
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(120))
    address: Mapped[str | None] = mapped_column(Text)

    visits: Mapped[list["Visit"]] = relationship("Visit", back_populates="patient", cascade="all,delete-orphan")
    medications: Mapped[list["Medication"]] = relationship("Medication", back_populates="patient", cascade="all,delete-orphan")

class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    visit_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    complaint: Mapped[str | None] = mapped_column(Text)
    diagnosis: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    patient: Mapped[Patient] = relationship("Patient", back_populates="visits")

class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    dosage: Mapped[str | None] = mapped_column(String(120))  # örn: 1x1
    start_date: Mapped[Date | None]
    end_date: Mapped[Date | None]
    instructions: Mapped[str | None] = mapped_column(Text)

    patient: Mapped[Patient] = relationship("Patient", back_populates="medications")
