from dotenv import load_dotenv
import os
from google import genai
import json 
from models import DocumentData

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=gemini_api_key)


def extract_text_from_document(text: str):

    prompt = f"""
You are an AI document extraction system.

Analyze the document text below and identify the type of document.

Return ONLY valid JSON.
Do not use markdown or ```.

Use EXACTLY this JSON structure:

{{
    "document_type": null,
    "name": null,
    "email": null,
    "phone": null,
    "skills": [],
    "experience": [],
    "projects": [],
    "education": [],
    "policy_details": null,
    "invoice_details": null
}}

Rules:

1. Identify the document type.

2. If the document is a resume or CV:
   - Extract name, email, phone, skills, experience,
     projects, and education.
   - For every experience item, "description" MUST be a list of strings.
   - For every project item, "description" MUST be a list of strings.
   - Never return "description" as a single string.
   - If there is only one description, still return it as a list
     containing one string.

3. If the document is a cover letter:
   - Extract available name and contact information.
   - Set policy_details to null.
   - Set invoice_details to null.

4. If the document is a policy or expense policy:
   - Extract the employee/person name if available.
   - Extract policy information into policy_details.
   - Set invoice_details to null.

5. For a policy document, policy_details must contain:

   {{
       "submission_deadline_days": null,
       "approval_threshold": null,
       "required_fields": []
   }}

6. If the document is an invoice:
   - Set name to null unless a person's name is explicitly present.
   - Extract invoice information into invoice_details.
   - Set policy_details to null.

7. For an invoice, invoice_details must contain EXACTLY these fields:

   {{
       "vendor_name": null,
       "invoice_number": null,
       "invoice_date": null,
       "due_date": null,
       "amount": null,
       "tax": null,
       "currency": null
   }}

8. For invoice amounts:
   - Return only numeric values.
   - Do not include currency symbols or text.
   - Example: "Rs. 65,000" becomes 65000.
   - Example: "₹65,000" becomes 65000.
   - Example: "Rs. 11,700" becomes 11700.

9. For approval_threshold:
   - Return only the numeric value.
   - Example: "Rs. 50,000" becomes 50000.

10. If information is missing:
    - Use null for single values.
    - Use [] for lists.

11. Do not invent information that is not present in the document.

12. The JSON field names MUST exactly match the JSON structure above.
    Never rename, misspell, or create alternative field names.

13. For an invoice:
    - "Invoice Date" must be stored in "invoice_date".
    - "Amount" must be stored in "amount".
    - "Tax" must be stored in "tax".
    - "Due Date" must be stored in "due_date".
    - "Vendor" must be stored in "vendor_name".

Document text:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    response_text = response.text.strip()

    # Remove Markdown code fences if Gemini adds them
    if response_text.startswith("```json"):
        response_text = response_text[7:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    data = json.loads(response_text)

    validated_data = DocumentData.model_validate(data)

    return validated_data.model_dump()