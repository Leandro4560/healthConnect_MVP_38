# app/models/clinical_record.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
# AÑADIDO: Importar UUID para claves foráneas
from sqlalchemy.dialects.postgresql import UUID as SQAlchemyUUID 

class ClinicalRecord(Base):
    __tablename__ = "clinical_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # Llaves foráneas
    # CORRECCIÓN CLAVE: Cambiar a UUID
    patient_id = Column(SQAlchemyUUID(as_uuid=True), ForeignKey("users.id"), index=True)
    # CORRECCIÓN CLAVE: Cambiar a UUID
    doctor_id = Column(SQAlchemyUUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    # Contenido del registro
    record_date = Column(DateTime, default=datetime.utcnow)
    diagnosis = Column(Text, nullable=False)
    treatment = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relaciones
    patient = relationship(
        "User", 
        foreign_keys=[patient_id], 
        back_populates="patient_records"
    )
    doctor = relationship(
        "User", 
        foreign_keys=[doctor_id], 
        back_populates="doctor_records"
    )

    def __repr__(self):
        return (f"<ClinicalRecord(id={self.id}, patient_id={self.patient_id}, "
                f"doctor_id={self.doctor_id}, date='{self.record_date}')>")