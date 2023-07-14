import streamlit as st
import streamlit_authenticator as stauth
from perry.authenticator import get_authentication_config


def chat_window():
    if "messages" not in st.session_state:
      st.session_state.messages = []
      with st.chat_message(avatar="assistant", name="Perry"):
        message = "Hi, I'm Perry! I'm a data analyst extraordinaire. What can I help you with today?"
        st.session_state.messages.append({"role": "assistant", "content": message})

    for message in st.session_state.messages:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
      st.session_state.messages.append({"role": "user", "content": prompt})
    
    if prompt:
      with st.chat_message(avatar="user", name=st.session_state["name"]):
        st.markdown(prompt)

    # st.session_state.messages.append({"role": "assistant", "content": full_response})


def login() -> stauth.Authenticate:
    authenticator = get_authentication_config()
    authenticator.login('Login', 'sidebar')
    return authenticator


def user_info(authenticator: stauth.Authenticate):
    name = st.session_state["name"]
    st.sidebar.write(f'Welcome *{name}*')
    authenticator.logout('Logout', 'sidebar', key='sidebar_logout')


if __name__ == "__main__":
    authenticator = login()
    
    if st.session_state["authentication_status"]:
      st.title("Perry - Data Analyst Extraordinaire")
      chat_window()
      user_info(authenticator)
      
    elif st.session_state["authentication_status"] is False: 
      st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
      st.warning('Please enter your username and password')