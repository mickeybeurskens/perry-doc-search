import io
import pathlib
import streamlit as st
import streamlit_authenticator as stauth
from perry.authenticator import get_authentication_config
from perry.utils import load_openai_api_key, get_production_env_path
from perry.messages import Message


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

def get_save_directory(user: str) -> pathlib.Path:
  save_dir = pathlib.Path(__file__).parent / "storage" / user
  if not save_dir.exists():
      save_dir.mkdir(parents=True)
  return save_dir

def remove_document(doc_path: pathlib.Path):
  if doc_path.exists():
    doc_path.unlink()

def chat_proto():
  # Current file
  load_openai_api_key(get_production_env_path())
  agent = st.session_state["agent"]

  if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

  if "messages" not in st.session_state:
    st.session_state.messages = []

  st.session_state.messages = agent.message_history.messages

  if st.session_state.messages:
    for message in st.session_state.messages:
      with st.chat_message(message.user):
        st.markdown(message.message)

  if prompt := st.chat_input("What is up?"):
      with st.chat_message("user"):
          st.markdown(prompt)

      with st.chat_message("assistant"):
          message_placeholder = st.empty()
          full_response = agent.answer_query(prompt)
          message_placeholder.markdown(full_response)
      # st.session_state.messages = agent.message_history.messages

def set_project_name():
  if f"project_name_{st.session_state.username}" not in st.session_state:
    st.session_state[f"project_name_{st.session_state.username}"] = ["default"]

  if "project_name" not in st.session_state:
    st.session_state["project_name"] = st.session_state[f"project_name_{st.session_state.username}"][0]

  st.sidebar.subheader("Choose a project")
  project = st.sidebar.selectbox("Project", st.session_state[f"project_name_{st.session_state.username}"])
  if project != st.session_state["project_name"]:
    st.session_state["project_name"] = project

  # Add project
  new_project = st.sidebar.text_input("New Project")
  if st.sidebar.button("Add Project"):
    if new_project not in st.session_state[f"project_name_{st.session_state.username}"]:
      st.session_state[f"project_name_{st.session_state.username}"].append(new_project)
      st.session_state["project_name"] = new_project
      st.sidebar.success(f"Project '{new_project}' added successfully")


  # Remove project (but never default)
  if st.sidebar.button("Remove Current Project"):
    if st.session_state["project_name"] != "default":
      cur_project = st.session_state["project_name"]
      st.session_state[f"project_name_{st.session_state.username}"].remove(st.session_state["project_name"])
      st.session_state["project_name"] = "default"
      st.sidebar.success(f"Project '{cur_project}' removed successfully")

  st.sidebar.success(f"Current project: {st.session_state.project_name}")


if __name__ == "__main__":
    # authenticator = login()
    
    # if st.session_state["authentication_status"]:
    st.title("Perry - Document Detective")
    st.sidebar.markdown("---")
    st.sidebar.markdown("---")
      # chat_proto()
      # user_info(authenticator)
      
    # elif st.session_state["authentication_status"] is False: 
    #   st.error('Username/password is incorrect')
    # elif st.session_state["authentication_status"] is None:
    #   st.warning('Please enter your username and password')