from models import DocumentData


def check_invoice_approval(
    data: DocumentData,
    approval_threshold: float
):

    if data.invoice_details is None:
        return {
            "status": "not_applicable",
            "message": "No invoice data available."
        }

    invoice_amount = data.invoice_details.amount

    if invoice_amount is None:
        return {
            "status": "unable_to_determine",
            "message": "Invoice amount is missing."
        }

    if invoice_amount > approval_threshold:
        return {
            "status": "approval_required",
            "invoice_amount": invoice_amount,
            "approval_threshold": approval_threshold,
            "message": (
                f"Manager approval is required because "
                f"the invoice amount ({invoice_amount}) exceeds "
                f"the approval threshold ({approval_threshold})."
            )
        }

    return {
        "status": "approval_not_required",
        "invoice_amount": invoice_amount,
        "approval_threshold": approval_threshold,
        "message": (
            f"Manager approval is not required because "
            f"the invoice amount ({invoice_amount}) does not exceed "
            f"the approval threshold ({approval_threshold})."
        )
    }