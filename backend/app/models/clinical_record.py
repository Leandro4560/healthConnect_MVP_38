
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

from sqlalchemy.dialects.postgresql import UUID as SQAlchemyUUID 

class ClinicalRecord(Base):
    __tablename__ = "clinical_records"

    id = Column(Integer, primary_key=True, index=True)
    

    patient_id = Column(SQAlchemyUUID(as_uuid=True), ForeignKey("users.id"), index=True)
 
    doctor_id = Column(SQAlchemyUUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    record_date = Column(DateTime, default=datetime.utcnow)
    diagnosis = Column(Text, nullable=False)
    treatment = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
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
