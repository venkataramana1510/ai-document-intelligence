import re
from models import DocumentData


def calculate_confidence(data: DocumentData):

    fields = {}

    document_type = (data.document_type or "").lower()

    # -------------------------------------------------
    # INVOICE
    # -------------------------------------------------

    if document_type == "invoice" and data.invoice_details:

        invoice = data.invoice_details

        if invoice.vendor_name:
            fields["vendor_name"] = {
                "value": invoice.vendor_name,
                "confidence": 0.95,
                "status": "high_confidence"
            }

        if invoice.invoice_number:
            fields["invoice_number"] = {
                "value": invoice.invoice_number,
                "confidence": 0.98,
                "status": "high_confidence"
            }

        if invoice.invoice_date:
            fields["invoice_date"] = {
                "value": invoice.invoice_date,
                "confidence": 0.95,
                "status": "high_confidence"
            }

        if invoice.due_date:
            fields["due_date"] = {
                "value": invoice.due_date,
                "confidence": 0.95,
                "status": "high_confidence"
            }

        if invoice.amount is not None:

            if invoice.amount > 0:
                fields["amount"] = {
                    "value": invoice.amount,
                    "confidence": 0.98,
                    "status": "high_confidence"
                }
            else:
                fields["amount"] = {
                    "value": invoice.amount,
                    "confidence": 0.30,
                    "status": "needs_review"
                }

        if invoice.tax is not None:

            if invoice.tax >= 0:
                fields["tax"] = {
                    "value": invoice.tax,
                    "confidence": 0.90,
                    "status": "high_confidence"
                }
            else:
                fields["tax"] = {
                    "value": invoice.tax,
                    "confidence": 0.30,
                    "status": "needs_review"
                }

        if invoice.currency:
            fields["currency"] = {
                "value": invoice.currency,
                "confidence": 0.90,
                "status": "high_confidence"
            }

    # -------------------------------------------------
    # RESUME / CV
    # -------------------------------------------------

    elif document_type in ["resume", "cv"]:

        if data.name:
            fields["name"] = {
                "value": data.name,
                "confidence": 0.95,
                "status": "high_confidence"
            }

        if data.email and "@" in data.email:
            fields["email"] = {
                "value": data.email,
                "confidence": 0.98,
                "status": "high_confidence"
            }

        if data.phone:

            digits = re.sub(r"\D", "", data.phone)

            if len(digits) >= 10:
                fields["phone"] = {
                    "value": data.phone,
                    "confidence": 0.95,
                    "status": "high_confidence"
                }

        if data.skills:
            fields["skills"] = {
                "value": data.skills,
                "confidence": 0.90,
                "status": "high_confidence"
            }

        if data.experience:
            fields["experience"] = {
                "value": data.experience,
                "confidence": 0.90,
                "status": "high_confidence"
            }

        if data.projects:
            fields["projects"] = {
                "value": data.projects,
                "confidence": 0.90,
                "status": "high_confidence"
            }

        if data.education:
            fields["education"] = {
                "value": data.education,
                "confidence": 0.90,
                "status": "high_confidence"
            }

    # -------------------------------------------------
    # POLICY
    # -------------------------------------------------

    elif "policy" in document_type or "expense" in document_type:

        if data.name:
            fields["name"] = {
                "value": data.name,
                "confidence": 0.95,
                "status": "high_confidence"
            }

        if data.policy_details:

            policy = data.policy_details

            if policy.submission_deadline_days is not None:
                fields["submission_deadline_days"] = {
                    "value": policy.submission_deadline_days,
                    "confidence": 0.95,
                    "status": "high_confidence"
                }

            if policy.approval_threshold is not None:
                fields["approval_threshold"] = {
                    "value": policy.approval_threshold,
                    "confidence": 0.98,
                    "status": "high_confidence"
                }

            if policy.required_fields:
                fields["required_fields"] = {
                    "value": policy.required_fields,
                    "confidence": 0.90,
                    "status": "high_confidence"
                }

    return fields