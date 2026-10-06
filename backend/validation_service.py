from models import DocumentData


def validate_document(data: DocumentData):

    errors = []
    warnings = []
    missing_fields = []

    document_type = (data.document_type or "").lower()

    # --------------------------------
    # Resume validation
    # --------------------------------

    if document_type in ["resume", "cv"]:

        if not data.name:
            missing_fields.append("Name is missing")

        if not data.email:
            missing_fields.append("Email is missing")

        if not data.phone:
            missing_fields.append("Phone is missing")

        if data.email and "@" not in data.email:
            errors.append("Invalid email format")

        if not data.skills:
            warnings.append("No skills found")

        if not data.education:
            warnings.append("No education information found")

        if not data.experience:
            warnings.append("No work experience found")

    # --------------------------------
    # Cover letter validation
    # --------------------------------

    elif document_type == "cover letter":

        if not data.name:
            warnings.append("Applicant name not found")

        if not data.email:
            warnings.append("Email not found")

    # --------------------------------
    # Expense policy validation
    # --------------------------------

    elif "expense" in document_type or "policy" in document_type:

        # Expense policies usually don't need
        # resume fields such as email, phone, skills, etc.

        if not data.name:
            warnings.append("No employee name found")
        if not data.policy_details: 
            warnings.append("No policy details found")
        else: 
            if data.policy_details.submission_deadline_days is None: 
                warnings.append( "Submission deadline not found" ) 
            if data.policy_details.approval_threshold is None: 
                warnings.append( "Approval threshold not found" ) 
            if not data.policy_details.required_fields: 
                warnings.append( "No required fields found" ) # -------------------------------- # Invoice validation
    elif document_type == "invoice":
        if not data.invoice_details:
            errors.append("Invoice details could not be extracted")
        else:
            if not data.invoice_details.vendor_name:
                missing_fields.append("Vendor name not found")
            if not data.invoice_details.invoice_number:
                missing_fields.append("Invoice number not found")
            if not data.invoice_details.invoice_date:
                missing_fields.append("Invoice date not found")
            if not data.invoice_details.due_date:
                missing_fields.append("Due date not found")
            if data.invoice_details.amount is None:
                missing_fields.append("Amount not found")
            if data.invoice_details.tax is None:
                missing_fields.append("Tax not found")
            if not data.invoice_details.currency:
                missing_fields.append("Currency not found")
            if data.invoice_details.amount is not None and data.invoice_details.amount < 0:
                errors.append("Invoice amount cannot be negative")
    # --------------------------------
    # Unknown document type
    # --------------------------------

    else:

        warnings.append(
            "Document type is not recognized. "
            "Validation rules could not be determined."
        )

    # --------------------------------
    # Determine overall status
    # --------------------------------

    if errors:
        status = "failed"

    elif missing_fields or warnings:
        status = "warning"

    else:
        status = "passed"

    return {
        "status": status,
        "missing_fields": missing_fields,
        "errors": errors,
        "warnings": warnings
    }