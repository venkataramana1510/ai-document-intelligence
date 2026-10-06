from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime,Text

from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=True)

    extracted_data = Column(Text, nullable=True)
    validation_result = Column(Text, nullable=True)
    confidence_result = Column(Text, nullable=True)
    approval_result = Column(Text, nullable=True)
    review_result = Column(Text, nullable=True)
    ingestion_result = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )