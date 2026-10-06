from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


file_path = "test_policy.pdf"

pdf = canvas.Canvas(file_path, pagesize=A4)

width, height = A4

y = height - 60

pdf.setFont("Helvetica-Bold", 18)
pdf.drawString(50, y, "Company Document Submission Policy")

y -= 40

pdf.setFont("Helvetica", 11)

policy_lines = [
    "1. Employees must submit invoices within 30 days of the invoice date.",
    "",
    "2. All invoices must contain:",
    "   - Employee name",
    "   - Invoice number",
    "   - Invoice date",
    "   - Amount",
    "   - Vendor name",
    "",
    "3. Missing required information may cause the invoice to be rejected.",
    "",
    "4. Invoices above Rs. 50,000 require manager approval.",
    "",
    "5. Employees should contact the finance department if they have",
    "   questions about invoice submission.",
    "",
    "6. Expense claims must be submitted within 15 days after the expense occurs.",
]

for line in policy_lines:
    pdf.drawString(50, y, line)
    y -= 20

pdf.save()

print(f"Created {file_path}")
