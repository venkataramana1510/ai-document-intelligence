from typing import List, Optional
from pydantic import BaseModel ,Field

class Experience(BaseModel):
    company:Optional[str] =None
    role:Optional[str]=None
    period:Optional[str]= None
    description:list[str] = Field(default_factory=list)
    
class Project(BaseModel):
    name:Optional[str]
    description:list[str] = Field(default_factory=list)
    tech_stack:list[str] = Field(default_factory=list)
    
class Education(BaseModel):
    institution:Optional[str] = None
    degree:Optional[str]= None
    period:Optional[str]=   None
    gpa:Optional[str]= None
class PolicyDetails(BaseModel):
    submission_deadline_days: Optional[int] = None
    approval_threshold: Optional[float] = None
    required_fields: list[str] = Field(default_factory=list)

class InvoiceDetails(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    amount: Optional[float] = None
    tax: Optional[float] = None
    currency: Optional[str] = None

    
class DocumentData(BaseModel):
    document_type: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    policy_details: Optional[PolicyDetails] = None
    invoice_details: Optional[InvoiceDetails] = None
    
class UploadResponse(BaseModel):
    filename: str
    text: str
    page_count: int
    ai_extraction: DocumentData
    validation_result: dict
    approval_result: dict | None = None
    confidence_result: dict
    review_result: dict
    ingestion_result: dict
    
