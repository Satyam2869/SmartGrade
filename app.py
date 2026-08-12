import streamlit as st
from PIL import Image

from auth import (
    login,
    create_session,
    student_login,
    create_student_session,
    register_admin,
)
from database import register_student

# -----------------------------
# Page Configuration
# -----------------------------
favicon = Image.open("favicon.png")

st.set_page_config(
    page_title="SmartGrade",
    page_icon=favicon,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Session Check
# -----------------------------
if st.session_state.get("logged_in", False):

    if st.session_state.get("role") == "Admin":
        st.switch_page("pages/1_Admin.py")
    else:
        st.switch_page("pages/2_Student.py")

# -----------------------------
# Login UI
# -----------------------------
st.markdown(
    """
    <h1 style='text-align:center;color:#1E88E5;'>
        🎓 SmartGrade System
    </h1>
    """,
    unsafe_allow_html=True,
)

st.write("")

admin_tab, student_tab, signup_tab = st.tabs(
    ["🛡️ Admin Login", "🎓 Student Login", "📝 Sign Up"]
)

# -----------------------------
# Admin Login (Username + Password)
# -----------------------------
with admin_tab:

    username = st.text_input(
        "Username",
        placeholder="Enter Admin Username",
        key="admin_username",
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter Password",
        key="admin_password",
    )

    if st.button("Login as Admin", use_container_width=True):

        username = username.strip()
        password = password.strip()

        if username == "" or password == "":
            st.warning("Please enter Username and Password.")
            st.stop()

        success, role, name = login(username, password)

        if success and role == "Admin":

            create_session(username, role, name)

            st.success(f"Welcome {name}!")
            st.switch_page("pages/1_Admin.py")

        else:

            st.error("Invalid Username or Password")

# -----------------------------
# Student Login (SAP ID + Email)
# -----------------------------
with student_tab:

    sap_id = st.text_input(
        "SAP ID / Roll Number",
        placeholder="Enter your SAP ID",
        key="student_sapid",
    )

    email = st.text_input(
        "Email",
        placeholder="Enter the email your teacher has on file",
        key="student_email",
    )

    if st.button("Login as Student", use_container_width=True):

        sap_id = sap_id.strip()
        email = email.strip()

        if sap_id == "" or email == "":
            st.warning("Please enter both SAP ID and Email.")
            st.stop()

        success, name = student_login(sap_id, email)

        if success:

            create_student_session(sap_id, name)

            st.success(f"Welcome {name}!")
            st.switch_page("pages/2_Student.py")

        else:

            st.error("SAP ID and Email don't match our records. Ask your teacher to confirm the email on file.")

# -----------------------------
# Sign Up (New Students & New Teachers/Admins)
# -----------------------------
with signup_tab:

    st.write("New here? Create your account below to save your info and log in right away.")

    su_student_tab, su_admin_tab = st.tabs(
        ["🎓 Student Sign Up", "🛡️ Teacher / Admin Sign Up"]
    )

    # --- Student Sign Up ---
    with su_student_tab:

        st.caption(
            "Register with your SAP ID and Email now — your teacher can grade "
            "you later and your marks will show up on this same account."
        )

        signup_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="signup_student_name",
        )

        signup_sap_id = st.text_input(
            "SAP ID / Roll Number",
            placeholder="Enter your SAP ID",
            key="signup_student_sapid",
        )

        signup_email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="signup_student_email",
        )

        signup_group = st.text_input(
            "Group (optional — your teacher can set/change this later)",
            placeholder="e.g. Group 4 / Batch A-3",
            key="signup_student_group",
        )

        if st.button(
            "Create Student Account",
            use_container_width=True,
            key="signup_student_btn",
        ):

            success, message = register_student(
                signup_sap_id.strip(),
                signup_name.strip(),
                signup_email.strip(),
                signup_group.strip(),
            )

            if success:
                st.success(message)
            else:
                st.error(message)

    # --- Teacher / Admin Sign Up ---
    with su_admin_tab:

        st.caption("Create a teacher/admin account to grade students and manage records.")

        signup_admin_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="signup_admin_name",
        )

        signup_username = st.text_input(
            "Choose a Username",
            placeholder="Enter a username",
            key="signup_admin_username",
        )

        signup_password = st.text_input(
            "Choose a Password",
            type="password",
            key="signup_admin_password",
        )

        signup_confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_admin_confirm",
        )

        if st.button(
            "Create Teacher / Admin Account",
            use_container_width=True,
            key="signup_admin_btn",
        ):

            if signup_password != signup_confirm_password:
                st.error("Passwords do not match.")
            elif signup_password.strip() == "":
                st.warning("Please enter a password.")
            else:
                success, message = register_admin(
                    signup_username.strip(),
                    signup_password.strip(),
                    signup_admin_name.strip(),
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)

st.markdown("---")

st.caption("© 2026 SmartGrade System")