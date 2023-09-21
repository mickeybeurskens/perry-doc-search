import io
import pathlib
import streamlit as st
import streamlit_authenticator as stauth
from perry.authenticator import get_authentication_config
from perry.utils import load_openai_api_key, get_production_env_path
from perry.agents.single_directory_vector import SingleDirectoryVectorAgent 
from perry.documents import save_document, DocumentMetadata, load_metadata_from_document_path
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

def upload_documents(user: str):
  st.sidebar.header("Upload Documents")
  uploaded_file = st.sidebar.file_uploader("Choose a file to upload", accept_multiple_files=False)
  if uploaded_file is not None:
     title = st.sidebar.text_input("Title")
     summary = st.sidebar.text_area("Summary")
     meta = DocumentMetadata(title=title, summary=summary, file_path=get_save_directory(user) / uploaded_file.name)
     if st.sidebar.button("Upload"):
      save_document(uploaded_file, meta)
      st.sidebar.success("Document uploaded successfully")

def remove_document(doc_path: pathlib.Path):
  if doc_path.exists():
    doc_path.unlink()

def show_upload_directory_structure(user: str):
  st.sidebar.header("Uploaded Documents")
  save_dir = get_save_directory(user)
  if "files_sidebar" not in st.session_state:
    st.session_state.files_sidebar = {}
  files = {}
  for file in save_dir.glob("*"):
    if file.is_file():
      if st.sidebar.button("Remove", key=file.stem):
        remove_document(file)
      else:
        files[file.stem] = file
        st.sidebar.subheader(file.stem)
        st.sidebar.write(file)
        metadata = load_metadata_from_document_path(file)
        st.sidebar.text("Metadata:")
        st.sidebar.write(metadata)
  st.session_state.files_sidebar = files


@st.cache_resource
def get_agent(user: str, project: str) -> SingleDirectoryVectorAgent:
  return SingleDirectoryVectorAgent(get_save_directory(user))

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

def load_new_agent():
  if "agent" not in st.session_state:
    st.session_state["agent"] = SingleDirectoryVectorAgent(get_save_directory(st.session_state["username"]))

  # set_project_name()

  st.sidebar.header("Perry Info")
  st.sidebar.subheader("Files seen by Perry:")
  if st.sidebar.button("Read new files", key="load_new_agent"):
    st.session_state["agent"] = SingleDirectoryVectorAgent(get_save_directory(st.session_state["username"]))
    st.sidebar.success("Files read successfully")

  for data in st.session_state["agent"].meta:
    st.sidebar.write(data.file_path)
  st.sidebar.markdown("---")
  

if __name__ == "__main__":
    authenticator = login()
    
    if st.session_state["authentication_status"]:
      st.title("Perry - Data Analyst Extraordinaire")
      # chat_window()
      load_new_agent()
      upload_documents(st.session_state["username"])
      st.sidebar.markdown("---")
      show_upload_directory_structure(st.session_state["username"])
      st.sidebar.markdown("---")
      chat_proto()
      user_info(authenticator)
      
    elif st.session_state["authentication_status"] is False: 
      st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
      st.warning('Please enter your username and password')