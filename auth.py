"""
auth.py
Authentication Module for SmartGrade System
"""

import pandas as pd
import streamlit as st
from config import USERS_FILE
from database import validate_student_login


# -----------------------------
# Load Users
# -----------------------------
def load_users():
    try:
        return pd.read_csv(USERS_FILE, dtype=str)

    except FileNotFoundError:
        return pd.DataFrame(
            columns=[
                "Username",
                "Password",
                "Role",
                "Name",
            ]
        )


# -----------------------------
# Save Users
# -----------------------------
def save_users(df):
    df.to_csv(USERS_FILE, index=False)


# -----------------------------
# Register Admin / Teacher
# -----------------------------
def register_admin(username, password, name):
    """
    Create a new Admin/Teacher account in users.csv so they can log in
    immediately afterwards. Returns (success, message).
    """
    username = str(username).strip()
    password = str(password).strip()
    name = str(name).strip()

    if not username or not password or not name:
        return False, "Full name, username, and password are all required."

    users = load_users()

    if (users["Username"].astype(str).str.lower() == username.lower()).any():
        return False, "That username is already taken. Please choose another."

    new_row = pd.DataFrame(
        [
            {
                "Username": username,
                "Password": password,
                "Role": "Admin",
                "Name": name,
            }
        ]
    )

    users = pd.concat([users, new_row], ignore_index=True)

    save_users(users)

    return True, "Account created successfully. You can now log in."


# -----------------------------
# Login
# -----------------------------
def login(username, password):

    users = load_users()

    user = users[
        (users["Username"] == str(username))
        &
        (users["Password"] == str(password))
    ]

    if user.empty:
        return False, None, None

    role = user.iloc[0]["Role"]
    name = user.iloc[0]["Name"]

    return True, role, name


# -----------------------------
# Student Login (Email + SAP ID)
# -----------------------------
def student_login(sap_id, email):
    """
    Students no longer have a Username/Password row in users.csv.
    Instead they log in with the SAP ID and Email that the admin linked
    to their grade record.
    """
    success, name = validate_student_login(sap_id, email)

    if not success:
        return False, None

    return True, name


# -----------------------------
# Create Session
# -----------------------------
def create_session(username, role, name):

    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.name = name


def create_student_session(sap_id, name):
    st.session_state.logged_in = True
    st.session_state.username = sap_id
    st.session_state.sap_id = sap_id
    st.session_state.role = "Student"
    st.session_state.name = name


# -----------------------------
# Logout
# -----------------------------
def logout():

    for key in [
        "logged_in",
        "username",
        "role",
        "name",
    ]:

        if key in st.session_state:
            del st.session_state[key]

    st.switch_page("app.py")


# -----------------------------
# Session Checks
# -----------------------------
def is_logged_in():

    return st.session_state.get(
        "logged_in",
        False
    )


def current_user():

    return st.session_state.get(
        "username",
        ""
    )


def current_name():

    return st.session_state.get(
        "name",
        ""
    )


def current_role():

    return st.session_state.get(
        "role",
        ""
    )


# -----------------------------
# Role Checks
# -----------------------------
def is_admin():

    return current_role() == "Admin"


def is_student():

    return current_role() == "Student"