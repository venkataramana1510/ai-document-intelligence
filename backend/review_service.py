from models import DocumentData


from models import DocumentData


def create_review_result(
    data: DocumentData,
    confidence_result: dict,
    validation_result: dict
):
    review_required = False
    reasons = []

    # Validation problems require review
    if validation_result["status"] in ["warning", "failed"]:
        review_required = True

        if validation_result["missing_fields"]:
            reasons.append("Required fields are missing.")

        if validation_result["errors"]:
            reasons.append("Validation errors were detected.")

        if validation_result["warnings"]:
            reasons.append("Validation warnings were detected.")

    # Low-confidence fields require review
    for field, details in confidence_result.items():

        if details["status"] == "needs_review":
            review_required = True
            reasons.append(
                f"{field} requires manual review."
            )

    if review_required:
        status = "review_required"
    else:
        status = "auto_approved"

    return {
        "status": status,
        "review_required": review_required,
        "reasons": reasons
    }
    