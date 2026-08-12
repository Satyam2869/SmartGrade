"""
SmartGrade System
Admin Dashboard
"""

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

from auth import (
    is_logged_in,
    is_admin,
    logout,
)

from config import (
    MAX_SLIDE,
    MAX_DELIVERY,
    MAX_QNA,
)

from database import (
    load_data,
    save_data,
    upsert_student,
    current_timestamp,
    get_group_students,
    search_student,
    update_student_info,
)

from grade import (
    calculate_total,
    calculate_percentage,
    calculate_grade,
)

from mail import send_student_report, send_group_reports
from utils.pdf_generator import generate_student_pdf

# ----------------------------------------------------
# Authentication
# ----------------------------------------------------

if not is_logged_in():
    st.error("Please login first.")
    st.stop()

if not is_admin():
    st.error("Access Denied")
    st.stop()

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

favicon = Image.open("favicon.png")

st.set_page_config(
    page_title="SmartGrade - Admin",
    page_icon=favicon,
    layout="wide",
)

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------

st.sidebar.title("🎓 SmartGrade")

st.sidebar.success(
    f"Welcome\n\n**{st.session_state.name}**"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True,
):
    logout()

st.sidebar.divider()

# ----------------------------------------------------
# Constants
# ----------------------------------------------------

MAX_GROUP_SIZE = 5

CRITERIA = [
    "Slide Quality",
    "Delivery & Body Language",
    "Q&A Handling",
]

# ----------------------------------------------------
# Session State
# ----------------------------------------------------

if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

if "group_size" not in st.session_state:
    st.session_state.group_size = 3

# ----------------------------------------------------
# Widget Keys
# ----------------------------------------------------

def widget_key(base, index):
    return f"{base}_{index}_{st.session_state.reset_counter}"

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------

st.title("📝 SmartGrade")
st.caption("Lightweight, offline, CSV-backed grading for live student presentations.")

tab_grade, tab_export, tab_reports = st.tabs(
    [
        "🎤 Live Grading Deck",
        "📊 Administrative Exporter",
        "📧 Reports",
    ]
)

# --------------------------------------------------------------------------
# TAB 1 — Live Grading Deck
# --------------------------------------------------------------------------

with tab_grade:

    st.subheader("Group Setup")

    col_group, col_size = st.columns([2, 1])

    with col_group:
        group_id = st.text_input(
            "Group Identifier",
            placeholder="e.g. Group 4 / Batch A-3"
        )

    with col_size:

        group_size = st.slider(
            "Number of students in group",
            min_value=1,
            max_value=MAX_GROUP_SIZE,
            value=st.session_state.group_size,
            key="group_size_slider",
        )

        st.session_state.group_size = group_size

    st.divider()

    st.subheader("Student Evaluation")

    student_entries = []

    running_total = 0

    for i in range(group_size):

        with st.container(border=True):

            st.markdown(f"### Student {i+1}")

            col1, col2, col3 = st.columns(3)

            with col1:
                name = st.text_input(
                    "Student Name",
                    key=widget_key("name", i)
                )

            with col2:
                sap_id = st.text_input(
                    "SAP ID",
                    key=widget_key("sapid", i)
                )

            with col3:
                email = st.text_input(
                    "Email",
                    placeholder="Leave blank to keep existing email on file",
                    key=widget_key("email", i)
                )

            mark_cols = st.columns(3)

            slide_quality = mark_cols[0].slider(
                "Slide Quality",
                0,
                MAX_SLIDE,
                5,
                key=widget_key("slide", i),
            )

            delivery = mark_cols[1].slider(
                "Delivery & Body Language",
                0,
                MAX_DELIVERY,
                5,
                key=widget_key("delivery", i),
            )

            qna = mark_cols[2].slider(
                "Q&A Handling",
                0,
                MAX_QNA,
                5,
                key=widget_key("qna", i),
            )

            feedback = st.text_area(
                "Faculty Feedback",
                key=widget_key("feedback", i),
                height=70,
            )

            total = calculate_total(
                slide_quality,
                delivery,
                qna,
            )

            percentage = calculate_percentage(total)

            grade = calculate_grade(total)

            running_total += total

            c1, c2, c3 = st.columns(3)

            c1.metric("Total", f"{total}/30")
            c2.metric("Percentage", f"{percentage}%")
            c3.metric("Grade", grade)

            student_entries.append(
                {
                    "Group": group_id.strip(),
                    "SAP_ID": sap_id.strip(),
                    "Name": name.strip(),
                    "Email": email.strip(),
                    "Slide_Quality": slide_quality,
                    "Delivery_Body_Language": delivery,
                    "QnA_Handling": qna,
                    "Total": total,
                    "Percentage": percentage,
                    "Grade": grade,
                    "Feedback": feedback.strip(),
                    "Last_Updated": current_timestamp(),
                }
            )

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Students",
        group_size,
    )

    col2.metric(
        "Group Total",
        running_total,
    )

    average = running_total / group_size if group_size else 0

    col3.metric(
        "Average",
        f"{average:.2f}",
    )

    if st.button(
        "💾 Save Group",
        type="primary",
        use_container_width=True,
    ):

        if not group_id.strip():

            st.error("Please enter Group ID.")

        elif any(
            not s["Name"] or not s["SAP_ID"]
            for s in student_entries
        ):

            st.error(
                "Each student must have both Name and SAP ID."
            )

        else:

            for student in student_entries:
                upsert_student(student)

            st.success(
                f"{len(student_entries)} student record(s) saved successfully."
            )

            st.session_state.reset_counter += 1

            st.rerun()

# --------------------------------------------------------------------------
# TAB 2 — Administrative Exporter
# --------------------------------------------------------------------------

with tab_export:

    st.subheader("📊 Student Records")

    df = load_data()

    if df.empty:

        st.info("No student records found.")

    else:

        search = st.text_input(
            "🔍 Search by Name or SAP ID"
        )

        if search:

            df = df[
                df["Name"].astype(str).str.contains(search, case=False)
                |
                df["SAP_ID"].astype(str).str.contains(search)
            ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader("📈 Analytics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Students",
                len(df)
            )

        with col2:
            st.metric(
                "Average",
                round(df["Total"].mean(), 2)
            )

        with col3:
            st.metric(
                "Highest",
                int(df["Total"].max())
            )

        with col4:
            st.metric(
                "Lowest",
                int(df["Total"].min())
            )

        st.divider()

        chart1, chart2 = st.columns(2)

        with chart1:

            fig = px.histogram(
                df,
                x="Grade",
                color="Grade",
                title="Grade Distribution",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        with chart2:

            fig = px.bar(
                df,
                x="Name",
                y="Total",
                color="Grade",
                title="Student Marks",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        st.divider()

        st.subheader("📥 Export")

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇ Download CSV",
            data=csv,
            file_name="presentation_grades.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.divider()

        st.subheader("✏️ Edit Student Info")

        st.caption("Fix a name, email, or group without touching marks.")

        edit_sap_id = st.text_input(
            "Enter SAP ID to edit",
            key="edit_sap_id_input",
        )

        if edit_sap_id.strip():

            match = search_student(edit_sap_id.strip())

            if match.empty:
                st.warning("No student found with that SAP ID.")
            else:
                record = match.iloc[-1]

                with st.form("edit_student_form"):

                    edit_name = st.text_input(
                        "Name",
                        value=str(record["Name"]),
                    )

                    edit_email = st.text_input(
                        "Email",
                        value=str(record["Email"]),
                    )

                    edit_group = st.text_input(
                        "Group",
                        value=str(record["Group"]),
                    )

                    if st.form_submit_button(
                        "💾 Save Changes",
                        use_container_width=True,
                    ):

                        success, message = update_student_info(
                            edit_sap_id.strip(),
                            name=edit_name,
                            email=edit_email,
                            group=edit_group,
                        )

                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

        st.divider()

        st.subheader("🗑 Delete Student")

        sap_delete = st.text_input(
            "Enter SAP ID"
        )

        if st.button(
            "Delete Student",
            type="secondary",
            use_container_width=True,
        ):

            if sap_delete.strip() == "":

                st.warning(
                    "Please enter a SAP ID."
                )

            else:

                df = df[
                    df["SAP_ID"].astype(str)
                    != sap_delete.strip()
                ]

                save_data(df)

                st.success(
                    "Student deleted successfully."
                )

                st.rerun()

# --------------------------------------------------------------------------
# TAB 3 — Reports (Email CSV / PDF results)
# --------------------------------------------------------------------------

with tab_reports:

    st.subheader("📧 Email Results to Students")

    df = load_data()

    if df.empty:
        st.info("No student records found yet.")
    else:
        group_options = sorted(df["Group"].dropna().astype(str).unique().tolist())

        if not group_options:
            st.info("No groups found yet.")
        else:
            selected_group = st.selectbox("Select group", group_options)

            roster = get_group_students(selected_group)

            if not roster:
                st.info("No students found in this group.")
            else:
                st.caption(
                    "Emails are fetched automatically from each student's "
                    "linked SAP ID — nothing to type here."
                )

                for student in roster:
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([2, 2, 2, 3])

                        c1.write(f"**{student['Name']}**")
                        c2.write(f"SAP ID: {student['SAP_ID']}")
                        c3.write(
                            f"Email: {student['Email'] if student['Email'] else '⚠️ not set'}"
                        )

                        with c4:
                            b1, b2 = st.columns(2)

                            if b1.button(
                                "Send CSV",
                                key=f"send_csv_{student['SAP_ID']}",
                                use_container_width=True,
                            ):
                                csv_bytes = pd.DataFrame([student]).to_csv(index=False).encode("utf-8")
                                success, error = send_student_report(student, csv_bytes=csv_bytes)

                                if success:
                                    st.success(f"CSV sent to {student['Name']}.")
                                else:
                                    st.error(f"Failed to send: {error}")

                            if b2.button(
                                "Send PDF",
                                key=f"send_pdf_{student['SAP_ID']}",
                                use_container_width=True,
                            ):
                                pdf_bytes = generate_student_pdf(student)
                                success, error = send_student_report(student, pdf_bytes=pdf_bytes)

                                if success:
                                    st.success(f"PDF sent to {student['Name']}.")
                                else:
                                    st.error(f"Failed to send: {error}")

                st.divider()

                st.subheader("📢 Send Results to Entire Group")

                missing_emails = [s for s in roster if not s["Email"]]

                if missing_emails:
                    st.warning(
                        f"{len(missing_emails)} student(s) in this group have no "
                        f"email on file and will be skipped: "
                        + ", ".join(s["Name"] for s in missing_emails)
                    )

                send_format = st.radio(
                    "Attachment format",
                    ["CSV", "PDF"],
                    horizontal=True,
                )

                if st.button(
                    f"📤 Send {send_format} to Entire Group",
                    type="primary",
                    use_container_width=True,
                ):
                    sendable = [s for s in roster if s["Email"]]

                    if not sendable:
                        st.error("No students in this group have an email on file.")
                    else:
                        csv_bytes_by_sap = None
                        pdf_bytes_by_sap = None

                        if send_format == "CSV":
                            csv_bytes_by_sap = {
                                s["SAP_ID"]: pd.DataFrame([s]).to_csv(index=False).encode("utf-8")
                                for s in sendable
                            }
                        else:
                            pdf_bytes_by_sap = {
                                s["SAP_ID"]: generate_student_pdf(s)
                                for s in sendable
                            }

                        results = send_group_reports(
                            sendable,
                            csv_bytes_by_sap=csv_bytes_by_sap,
                            pdf_bytes_by_sap=pdf_bytes_by_sap,
                        )

                        ok_count = sum(1 for _, _, ok, _ in results if ok)
                        st.success(f"Sent to {ok_count} / {len(results)} students.")

                        failures = [(name, err) for _, name, ok, err in results if not ok]
                        if failures:
                            st.error(
                                "Failed for: "
                                + ", ".join(f"{name} ({err})" for name, err in failures)
                            )

# --------------------------------------------------------------------------
# Footer
# --------------------------------------------------------------------------

st.divider()

st.caption(
    "© 2026 SmartGrade System | Developed using Streamlit"
)

