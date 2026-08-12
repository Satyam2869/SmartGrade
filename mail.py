"""
mail.py
--------
Email sending utilities for SmartGrade System.

Uses Python's built-in smtplib — no external email service required.
Configure SMTP_SERVER / SENDER_EMAIL / SENDER_PASSWORD in config.py.
"""

import smtplib
from email.message import EmailMessage

from config import (
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    SENDER_NAME,
)


def _build_message(to_email, subject, body, attachments=None):
    """
    attachments: optional list of (filename, bytes, mime_type) tuples.
    """
    msg = EmailMessage()
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    for filename, file_bytes, mime_type in (attachments or []):
        maintype, subtype = mime_type.split("/", 1)
        msg.add_attachment(
            file_bytes,
            maintype=maintype,
            subtype=subtype,
            filename=filename,
        )

    return msg


def send_email(to_email, subject, body, attachments=None):
    """
    Send a single email. Returns (success: bool, error_message: str or None).
    """
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return False, (
            "Email is not configured yet. Set SENDER_EMAIL and "
            "SENDER_PASSWORD in config.py."
        )

    if not to_email:
        return False, "No email address on file for this student."

    msg = _build_message(to_email, subject, body, attachments)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True, None
    except Exception as e:
        return False, str(e)


def send_student_report(student, csv_bytes=None, pdf_bytes=None):
    """
    Email one student their result.
    student: dict with at least Name, SAP_ID, Email, Total, Percentage, Grade.
    """
    name = student.get("Name", "Student")
    sap_id = student.get("SAP_ID", "")
    email = student.get("Email", "")

    subject = f"Your Presentation Result — {name}"
    body = (
        f"Hi {name},\n\n"
        f"Here is your presentation evaluation (SAP ID: {sap_id}):\n\n"
        f"Total: {student.get('Total', '')} / 30\n"
        f"Percentage: {student.get('Percentage', '')}%\n"
        f"Grade: {student.get('Grade', '')}\n\n"
        f"Feedback: {student.get('Feedback', '') or '(none)'}\n\n"
        f"Regards,\n{SENDER_NAME}"
    )

    attachments = []
    if csv_bytes is not None:
        attachments.append((f"{sap_id}_result.csv", csv_bytes, "text/csv"))
    if pdf_bytes is not None:
        attachments.append((f"{sap_id}_result.pdf", pdf_bytes, "application/pdf"))

    return send_email(email, subject, body, attachments)


def send_group_reports(group_students, csv_bytes_by_sap=None, pdf_bytes_by_sap=None):
    """
    Email every student in a group their individual result.
    Returns a list of (sap_id, name, success, error) for a results table.
    """
    results = []

    for student in group_students:
        sap_id = student["SAP_ID"]

        csv_bytes = (csv_bytes_by_sap or {}).get(sap_id)
        pdf_bytes = (pdf_bytes_by_sap or {}).get(sap_id)

        success, error = send_student_report(student, csv_bytes, pdf_bytes)

        results.append((sap_id, student.get("Name", ""), success, error))

    return results
