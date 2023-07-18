import io
import pathlib
import streamlit as st
import streamlit_authenticator as stauth
from perry.authenticator import get_authentication_config
from perry.utils import load_openai_api_key, get_production_env_path
from perry.agents.single_directory_vector import SingleDirectoryVectorAgent 
from perry.documents import save_document, DocumentMetadata, load_metadata_from_document_path



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
  st.session_state["files_sidebar"] = files


@st.cache_resource
def get_agent(user: str) -> SingleDirectoryVectorAgent:
  return SingleDirectoryVectorAgent(get_save_directory(user))

def chat_proto():
  # Current file
  load_openai_api_key(get_production_env_path())
  agent = get_agent(st.session_state["username"])

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
          full_response = agent.answer_query(st.session_state.messages[-1]["content"])
          message_placeholder.markdown(full_response)
      st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    authenticator = login()
    
    if st.session_state["authentication_status"]:
      st.title("Perry - Data Analyst Extraordinaire")
      # chat_window()
      chat_proto()
      upload_documents(st.session_state["username"])
      st.sidebar.markdown("---")
      show_upload_directory_structure(st.session_state["username"])
      st.sidebar.markdown("---")
      user_info(authenticator)
      
    elif st.session_state["authentication_status"] is False: 
      st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
      st.warning('Please enter your username and password')