import streamlit as st
import streamlit_authenticator as stauth
from perry.authenticator import get_authentication_config


if __name__ == "__main__":
    st.title("Perry - Data Analyst Extraordinaire")
    authenticator = get_authentication_config()
    name, authentication_status, username = authenticator.login('Login', 'main')
    st.write(f'Welcome *{name}*')
    st.write(f'Username *{username}*')
    st.write(f'Authentication status *{authentication_status}*')


    if authentication_status:
      authenticator.logout('Logout', 'main', key='unique_key')
      st.write(f'Welcome *{name}*')
      st.title('Some content')
    elif authentication_status is False: 
      st.error('Username/password is incorrect')
    elif authentication_status is None:
      st.warning('Please enter your username and password')