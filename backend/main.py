
from pydantic import BaseModel
from rag.qa_service import answer_question
from models import DocumentData, UploadResponse
from validation_service import validate_document
from fastapi import FastAPI,UploadFile, File,Depends    
from testApi import extract_text_from_document
from pypdf import PdfReader
from confidence_service import calculate_confidence
from rag.ingestion_service import ingest_document
from business_rules_service import check_invoice_approval
from rag.policy_service import get_approval_threshold
from fastapi.middleware.cors import CORSMiddleware
from review_service import create_review_result
import json 
from sqlalchemy.orm import Session
from database import get_db
from database_models import Document


class QuestionRequest(BaseModel):
        question: str
        source_file: str | None = None
        
class ReviewRequest(BaseModel):
    document_data: DocumentData
app =  FastAPI(
            title="My API",
        )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class DocumentReviewRequest(BaseModel):
    document_data: DocumentData
    review_status: str

@app.get("/")
def read_root():
        return{"hello":"world"}

@app.post("/upload" ,response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
            reader = PdfReader(file.file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            page_count = len(reader.pages)
            extracted_data = extract_text_from_document(text)
            document_data = DocumentData.model_validate(extracted_data)
            validated_data = validate_document(document_data)
            approval_result = None

            if document_data.document_type == "invoice":
                approval_threshold = get_approval_threshold()
                approval_result = check_invoice_approval(
                    document_data,
                    approval_threshold=approval_threshold
                )
            confidence_result = calculate_confidence(document_data)
            review_result = create_review_result(
                document_data,
                confidence_result,
                validated_data
            )
            ingest_result = ingest_document(
    text,
    file.filename
)
            db_document = Document(
    filename=file.filename,
    document_type=document_data.document_type,

    extracted_data=json.dumps(
        document_data.model_dump()
    ),

    validation_result=json.dumps(
        validated_data
    ),

    confidence_result=json.dumps(
        confidence_result
    ),

    approval_result=json.dumps(
        approval_result
    ) if approval_result else None,

    review_result=json.dumps(
        review_result
    ),

    ingestion_result=json.dumps(
        ingest_result
    )
)

            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            
            return {"filename": file.filename, 
                    "text": text,
                    "page_count": page_count,
                    "ai_extraction": extracted_data ,
                    "validation_result": validated_data,
                    "confidence_result": confidence_result,
                    "review_result": review_result,
                    "ingestion_result": ingest_result,
                    "approval_result": approval_result,
                    }
        

@app.post("/review/approve")
def approve_review(request: ReviewRequest):

    document_data = request.document_data

    # Validate the corrected document
    validation_result = validate_document(document_data)

    # Check invoice business rules
    approval_result = None

    if document_data.document_type == "invoice":

        approval_threshold = get_approval_threshold()

        approval_result = check_invoice_approval(
            document_data,
            approval_threshold=approval_threshold
        )

    return {
        "status": "approved",
        "document_data": document_data.model_dump(),
        "validation_result": validation_result,
        "approval_result": approval_result
    }
@app.post("/ask")
def ask_question(request: QuestionRequest):
    result = answer_question(
        request.question,
        request.source_file
    )
    return result

@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.id.desc()).all()

    result = []

    for document in documents:
        result.append({
            "id": document.id,
            "filename": document.filename,
            "document_type": document.document_type,
            "extracted_data": json.loads(document.extracted_data)
                if document.extracted_data else None,
            "validation_result": json.loads(document.validation_result)
                if document.validation_result else None,
            "confidence_result": json.loads(document.confidence_result)
                if document.confidence_result else None,
            "approval_result": json.loads(document.approval_result)
                if document.approval_result else None,
            "review_result": json.loads(document.review_result)
                if document.review_result else None,
            "ingestion_result": json.loads(document.ingestion_result)
                if document.ingestion_result else None,
            "created_at": document.created_at
        })

    return result

@app.get("/documents/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        return {
            "error": "Document not found"
        }

    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,

        "extracted_data": json.loads(document.extracted_data)
        if document.extracted_data else None,

        "validation_result": json.loads(document.validation_result)
        if document.validation_result else None,

        "confidence_result": json.loads(document.confidence_result)
        if document.confidence_result else None,

        "approval_result": json.loads(document.approval_result)
        if document.approval_result else None,

        "review_result": json.loads(document.review_result)
        if document.review_result else None,

        "ingestion_result": json.loads(document.ingestion_result)
        if document.ingestion_result else None,

        "created_at": document.created_at
    }
    
@app.put("/documents/{document_id}/review")
def update_document_review(
    document_id: int,
    request: DocumentReviewRequest,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        return {
            "error": "Document not found"
        }

    # Update extracted data after human correction
    document.extracted_data = json.dumps(
        request.document_data.model_dump()
    )

    # Re-run validation
    validation_result = validate_document(
        request.document_data
    )

    document.validation_result = json.dumps(
        validation_result
    )

    # Update review result
    review_result = {
        "status": request.review_status,
        "review_required": False,
        "reasons": []
    }

    document.review_result = json.dumps(
        review_result
    )

    db.commit()
    db.refresh(document)

    return {
        "message": "Document review updated successfully",
        "document_id": document.id,
        "review_result": review_result,
        "validation_result": validation_result
    }
    
@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        return {
            "error": "Document not found"
        }

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }