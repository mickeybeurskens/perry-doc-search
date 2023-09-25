import streamlit as st
import requests


def get_server_url():
    return "http://backend:8000"


def get_users_url():
    return f"{get_server_url()}/users"


def get_token_url():
    return f"{get_users_url()}/token"


def get_register_url():
    return f"{get_users_url()}/register"



def login():

    # Construct call curl -X 'POST' \
    #   'http://localhost:8000/users/token' \
    #   -H 'accept: application/json' \
    #   -H 'Content-Type: application/x-www-form-urlencoded' \
    #   -d 'grant_type=&username=string&password=string&scope=&client_id=&client_secret='


    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        response = requests.post(
            get_token_url(),
            headers={"accept": "application/json"},
            data={"username": username, "password": password}
        )
        st.write(response)
        st.write(username)
        st.write(password)
        if response.status_code == 200:
            st.session_state["authentication_status"] = True
            return response.json()["authenticator"]
        else:
            st.session_state["authentication_status"] = False
    else:
        st.session_state["authentication_status"] = None


def create_user():
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Create"):
        response = requests.post(
            get_register_url(),
            headers={"accept": "application/json"},
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            st.session_state["authentication_status"] = True
            return response.json()
        else:
            st.session_state["authentication_status"] = False
    else:
        st.session_state["authentication_status"] = None


if __name__ == "__main__":
    authenticator = login()
    st.title("Perry - Document Detective")
    
    if st.session_state["authentication_status"]:
      st.text('Welcome to Perry')
    else:
      st.text('Please login')
      # chat_proto()
      # user_info(authenticator)
      
    # elif st.session_state["authentication_status"] is False: 
    #   st.error('Username/password is incorrect')
    # elif st.session_state["authentication_status"] is None:
    #   st.warning('Please enter your username and password')