"""
utils/pdf_generator.py
------------------------
Builds a one-page PDF result sheet for a single student, using fpdf2.
"""

from fpdf import FPDF


def generate_student_pdf(student: dict) -> bytes:
    """
    student: dict with Group, SAP_ID, Name, Slide_Quality,
    Delivery_Body_Language, QnA_Handling, Total, Percentage, Grade, Feedback.
    Returns the PDF file as bytes.
    """
    pdf = FPDF(format="A4")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "SmartGrade - Presentation Result", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 12)

    rows = [
        ("Name", student.get("Name", "")),
        ("SAP ID", student.get("SAP_ID", "")),
        ("Group", student.get("Group", "")),
    ]
    for label, value in rows:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(40, 8, f"{label}:")
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, str(value), ln=True)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Evaluation Breakdown", ln=True)

    pdf.set_font("Helvetica", "", 12)
    criteria = [
        ("Slide Quality", student.get("Slide_Quality", "")),
        ("Delivery & Body Language", student.get("Delivery_Body_Language", "")),
        ("Q&A Handling", student.get("QnA_Handling", "")),
    ]
    for label, value in criteria:
        pdf.cell(70, 8, label)
        pdf.cell(0, 8, f"{value} / 10", ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(70, 8, "Total")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"{student.get('Total', '')} / 30", ln=True)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(70, 8, "Percentage")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"{student.get('Percentage', '')} %", ln=True)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(70, 8, "Grade")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"{student.get('Grade', '')}", ln=True)

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Faculty Feedback", ln=True)
    pdf.set_font("Helvetica", "", 12)
    feedback = str(student.get("Feedback", "") or "No feedback provided.")
    pdf.multi_cell(0, 8, feedback)

    return bytes(pdf.output())
