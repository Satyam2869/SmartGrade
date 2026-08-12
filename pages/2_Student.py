import streamlit as st
import pandas as pd
from PIL import Image

from auth import (
    is_logged_in,
    is_student,
    current_user,
    current_name,
    logout,
)

from database import load_data

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

favicon = Image.open("favicon.png")

st.set_page_config(
    page_title="SmartGrade - Student",
    page_icon=favicon,
    layout="wide",
)

# ----------------------------------------------------
# Security Check
# ----------------------------------------------------

if not is_logged_in():
    st.error("Please login first.")
    st.stop()

if not is_student():
    st.error("Access Denied")
    st.stop()

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------

st.sidebar.title("🎓 SmartGrade")

st.sidebar.success(f"Welcome\n\n**{current_name()}**")

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True,
):
    logout()

# ----------------------------------------------------
# Header
# ----------------------------------------------------

st.title("🎓 Student Dashboard")
st.caption("View your presentation evaluation and faculty feedback.")

# ----------------------------------------------------
# Load Student Data
# ----------------------------------------------------

df = load_data()

student = df[df["SAP_ID"].astype(str) == str(current_user())]

if student.empty:
    st.warning("No marks found for your account.")
    st.stop()

student = student.iloc[0]

# ----------------------------------------------------
# Dashboard Cards
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Group", student["Group"])

with c2:
    st.metric("Total", f"{student['Total']} / 30")

with c3:
    st.metric("Percentage", f"{student['Percentage']} %")

with c4:
    st.metric("Grade", student["Grade"])

st.divider()

# ----------------------------------------------------
# Student Information
# ----------------------------------------------------

st.subheader("👤 Student Information")

left, right = st.columns(2)

with left:
    st.write(f"**Name:** {student['Name']}")
    st.write(f"**SAP ID:** {student['SAP_ID']}")

with right:
    st.write(f"**Last Updated:** {student['Last_Updated']}")

st.divider()

# ----------------------------------------------------
# Marks Breakdown
# ----------------------------------------------------

st.subheader("📊 Presentation Evaluation")

criteria = [
    ("Slide Quality", "Slide_Quality"),
    ("Delivery & Body Language", "Delivery_Body_Language"),
    ("Q&A Handling", "QnA_Handling"),
]

for title, column in criteria:

    marks = int(student[column])

    st.write(f"### {title}")
    st.progress(marks / 10)
    st.write(f"**Marks:** {marks} / 10")
    st.write("")

st.divider()

# ----------------------------------------------------
# Faculty Feedback
# ----------------------------------------------------

st.subheader("💬 Faculty Feedback")

feedback = student["Feedback"]

if pd.isna(feedback) or str(feedback).strip() == "":
    st.info("No feedback available.")
else:
    st.success(feedback)

st.divider()

# ----------------------------------------------------
# Footer
# ----------------------------------------------------

st.caption("© 2026 SmartGrade System")

