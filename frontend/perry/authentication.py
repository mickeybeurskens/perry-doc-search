import os
import streamlit as st
from perry.requests import RequestManager


def session_login_wrapper(handle_page_state):
    API_BASE_URL = os.getenv(
        "API_BASE_URL", "http://backend:8000"
    )  # Get from environment variable
    request_manager = RequestManager(API_BASE_URL)
    initialize_session_state()

    if st.session_state["authentication_status"]:
        handle_page_state(request_manager)
        handle_logout(request_manager)
    else:
        handle_login(request_manager)


def initialize_session_state():
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "jwt_token" not in st.session_state:
        st.session_state["jwt_token"] = None


def handle_registration(user_manager):
    st.sidebar.header("Register")
    username_reg = st.sidebar.text_input("New Username")
    password_reg = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Register"):
        response = user_manager.register(username_reg, password_reg)
        st.sidebar.write(
            "Successfully registered!"
            if response.status_code == 200
            else "Registration failed. Username may already exist."
        )


def display_user_info(request_manager: RequestManager):
    user_info = request_manager.get_user_info(st.session_state["jwt_token"])
    if user_info.status_code == 200:
        user_info = user_info.json()
        st.sidebar.write(f"Welcome back **{user_info['username']}**!")


def handle_login(user_manager):
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        response = user_manager.login(username, password)
        if response.status_code == 200:
            st.session_state["authentication_status"] = True
            st.session_state["jwt_token"] = response.json()["access_token"]
            st.rerun()  # Force rerun to update the sidebar
        else:
            st.session_state["authentication_status"] = False
            st.sidebar.write("Login failed.")


def handle_logout(request_manager):
    display_user_info(request_manager)
    if st.sidebar.button("Logout"):
        st.session_state["authentication_status"] = False
        st.session_state["jwt_token"] = None
        st.rerun()
