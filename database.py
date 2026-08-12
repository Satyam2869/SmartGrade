"""
database.py
------------
Handles all CSV operations for SmartGrade System.
"""

import os
import pandas as pd
from datetime import datetime

from config import CSV_FILE, COLUMNS


# -----------------------------
# Create CSV if not exists
# -----------------------------
def initialize_database():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)


# -----------------------------
# Load Data
# -----------------------------
def load_data():
    initialize_database()

    try:
        df = pd.read_csv(CSV_FILE, dtype={"SAP_ID": str})

    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLUMNS)

    except FileNotFoundError:
        return pd.DataFrame(columns=COLUMNS)

    # Add missing columns automatically
    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""

    # Keep only required columns
    return df[COLUMNS]


# -----------------------------
# Save Data
# -----------------------------
def save_data(df):
    df.to_csv(CSV_FILE, index=False)


# -----------------------------
# Add or Update Student
# -----------------------------
def upsert_student(student):
    """
    Insert or update a student's record.

    Email linking rule: once an SAP ID has an email on file, that email is
    kept automatically on every future re-grade unless the admin explicitly
    types a new one. This is what makes the SAP ID <-> Email link
    "permanent unless edited".
    """
    df = load_data()

    sap = str(student["SAP_ID"])

    existing = df[df["SAP_ID"].astype(str) == sap]

    incoming_email = str(student.get("Email", "") or "").strip()

    if not incoming_email and not existing.empty:
        old_email = str(existing.iloc[-1].get("Email", "") or "").strip()
        if old_email:
            student["Email"] = old_email

    df = df[df["SAP_ID"].astype(str) != sap]

    df = pd.concat([df, pd.DataFrame([student])], ignore_index=True)

    save_data(df)


# -----------------------------
# Student Self Sign Up
# -----------------------------
def register_student(sap_id, name, email, group=""):
    """
    Let a student create their own (ungraded) record so they can log in
    with SAP ID + Email right away, before any grading has happened.
    A teacher grading them later will fill in marks on this same row
    (matched by SAP ID) rather than creating a duplicate.
    Returns (success, message).
    """
    sap_id = str(sap_id).strip()
    name = str(name).strip()
    email = str(email).strip()
    group = str(group).strip()

    if not sap_id or not name or not email:
        return False, "Name, SAP ID, and Email are all required."

    if student_exists(sap_id):
        return False, (
            "This SAP ID is already registered. Please log in instead, "
            "or contact your teacher if you think this is a mistake."
        )

    student = {
        "Group": group,
        "SAP_ID": sap_id,
        "Name": name,
        "Email": email,
        "Slide_Quality": 0,
        "Delivery_Body_Language": 0,
        "QnA_Handling": 0,
        "Total": 0,
        "Percentage": 0,
        "Grade": "-",
        "Feedback": "",
        "Last_Updated": current_timestamp(),
    }

    upsert_student(student)

    return True, "Registration successful! You can now log in with your SAP ID and Email."


# -----------------------------
# Email Lookup
# -----------------------------
def get_student_email(sap_id):
    """Return the email on file for an SAP ID, or '' if none/not found."""
    df = load_data()

    match = df[df["SAP_ID"].astype(str) == str(sap_id)]

    if match.empty:
        return ""

    return str(match.iloc[-1].get("Email", "") or "").strip()


# -----------------------------
# Student Login Validation (Email + SAP ID)
# -----------------------------
def validate_student_login(sap_id, email):
    """
    Check the grade sheet for a row where SAP_ID matches and the stored
    Email matches (case-insensitive). Returns (success, name).
    """
    df = load_data()

    match = df[df["SAP_ID"].astype(str) == str(sap_id).strip()]

    if match.empty:
        return False, None

    stored_email = str(match.iloc[-1].get("Email", "") or "").strip().lower()
    typed_email = str(email or "").strip().lower()

    if stored_email and stored_email == typed_email:
        return True, match.iloc[-1].get("Name", "")

    return False, None


# -----------------------------
# Group Roster (for bulk emailing)
# -----------------------------
def get_group_students(group_id):
    """
    Return one row per student (SAP_ID, Name, Email, Total, Percentage,
    Grade) for everyone currently recorded in the given group.
    """
    df = load_data()

    group_df = df[df["Group"].astype(str) == str(group_id)]

    group_df = group_df.drop_duplicates(subset="SAP_ID", keep="last")

    cols = [
        "SAP_ID",
        "Name",
        "Email",
        "Group",
        "Slide_Quality",
        "Delivery_Body_Language",
        "QnA_Handling",
        "Total",
        "Percentage",
        "Grade",
        "Feedback",
    ]

    return group_df[cols].to_dict("records")


# -----------------------------
# Add Multiple Students
# -----------------------------
def upsert_students(student_list):
    for student in student_list:
        upsert_student(student)


# -----------------------------
# Search Student
# -----------------------------
def search_student(sap_id):
    df = load_data()

    return df[df["SAP_ID"].astype(str) == str(sap_id)]


# -----------------------------
# Edit Student Info (Name/Email/Group only — marks untouched)
# -----------------------------
def update_student_info(sap_id, name=None, email=None, group=None):
    """
    Update a student's Name, Email, and/or Group without touching their
    marks. Pass None, or leave a field blank, to leave that field
    unchanged. Returns (success, message).
    """
    sap_id = str(sap_id).strip()

    df = load_data()

    match = df["SAP_ID"].astype(str) == sap_id

    if not match.any():
        return False, "No student found with that SAP ID."

    if name is not None and str(name).strip():
        df.loc[match, "Name"] = str(name).strip()

    if email is not None and str(email).strip():
        df.loc[match, "Email"] = str(email).strip()

    if group is not None and str(group).strip():
        df.loc[match, "Group"] = str(group).strip()

    save_data(df)

    return True, "Student info updated successfully."


# -----------------------------
# Delete Student
# -----------------------------
def delete_student(sap_id):
    df = load_data()

    df = df[df["SAP_ID"].astype(str) != str(sap_id)]

    save_data(df)


# -----------------------------
# Update Student
# -----------------------------
def update_student(student):
    upsert_student(student)


# -----------------------------
# Student Exists
# -----------------------------
def student_exists(sap_id):
    df = load_data()

    return any(df["SAP_ID"].astype(str) == str(sap_id))


# -----------------------------
# Statistics
# -----------------------------
def total_students():
    return len(load_data())


def total_groups():
    df = load_data()

    if df.empty:
        return 0

    return df["Group"].nunique()


def average_marks():
    df = load_data()

    if df.empty:
        return 0

    return round(df["Total"].mean(), 2)


def highest_marks():
    df = load_data()

    if df.empty:
        return 0

    return df["Total"].max()


def lowest_marks():
    df = load_data()

    if df.empty:
        return 0

    return df["Total"].min()


# -----------------------------
# Timestamp
# -----------------------------
def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")