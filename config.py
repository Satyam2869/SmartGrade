"""
config.py
Configuration file for SmartGrade System
"""

# -----------------------------
# CSV Files
# -----------------------------

CSV_FILE = "presentation_grades.csv"
USERS_FILE = "users.csv"

# -----------------------------
# Maximum Marks
# -----------------------------

MAX_SLIDE = 10
MAX_DELIVERY = 10
MAX_QNA = 10

TOTAL_MARKS = 30

# -----------------------------
# CSV Columns
# -----------------------------

COLUMNS = [
    "Group",
    "SAP_ID",
    "Name",
    "Email",
    "Slide_Quality",
    "Delivery_Body_Language",
    "QnA_Handling",
    "Total",
    "Percentage",
    "Grade",
    "Feedback",
    "Last_Updated",
]

# -----------------------------
# Email / SMTP Settings
# -----------------------------
# For Gmail: create an "App Password" (Google Account -> Security ->
# 2-Step Verification -> App passwords) and put it in SENDER_PASSWORD.
# Do NOT use your normal Gmail login password here.
#
# IMPORTANT: never commit real values here to a public repo. Fill these
# in locally after cloning, and keep this file out of version control
# once you've done that (see .gitignore).

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = ""        # e.g. "yourclass@gmail.com"
SENDER_PASSWORD = ""     # the 16-character Gmail App Password
SENDER_NAME = "SmartGrade System"
