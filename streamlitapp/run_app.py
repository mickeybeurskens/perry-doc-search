import streamlit as st
import streamlit_authenticator as stauth
from perry.authenticator import get_authentication_config
import openai
from perry.utils import load_openai_api_key, get_production_env_path

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


def chat_proto():
  # Current file
  load_openai_api_key(get_production_env_path())

  if "openai_model" not in st.session_state:
      st.session_state["openai_model"] = "gpt-3.5-turbo"

  if "messages" not in st.session_state:
      st.session_state.messages = []

  for message in st.session_state.messages:
      with st.chat_message(message["role"]):
          st.markdown(message["content"])

  if prompt := st.chat_input("What is up?"):
      st.session_state.messages.append({"role": "user", "content": prompt})
      with st.chat_message("user"):
          st.markdown(prompt)

      with st.chat_message("assistant"):
          message_placeholder = st.empty()
          full_response = ""
          for response in openai.ChatCompletion.create(
              model=st.session_state["openai_model"],
              messages=[
                  {"role": m["role"], "content": m["content"]}
                  for m in st.session_state.messages
              ],
              stream=True,
          ):
              full_response += response.choices[0].delta.get("content", "")
              message_placeholder.markdown(full_response + "▌")
          message_placeholder.markdown(full_response)
      st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    authenticator = login()
    
    if st.session_state["authentication_status"]:
      st.title("Perry - Data Analyst Extraordinaire")
      # chat_window()
      chat_proto()
      user_info(authenticator)
      
    elif st.session_state["authentication_status"] is False: 
      st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
      st.warning('Please enter your username and password')