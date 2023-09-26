import streamlit as st
import pandas as pd
from perry.requests import RequestManager
from perry.authentication import session_login_wrapper


def upload_document(request_manager):
    st.title("Upload Document")
    document = st.file_uploader("Upload your PDF files here.")
    description = st.text_input("Enter a description for the document.")
    if document:
        st.write("Filename:", document)
        if document.type != "application/pdf":
            st.write("Please upload a PDF file.")
            return
        if document.size > 10000000:
            st.write("Please upload a file smaller than 10MB.")
            return
        if st.button("Upload"):
          document_response = request_manager.upload_document(
              st.session_state["jwt_token"], document
          )
          update_response = request_manager.update_document(
                st.session_state["jwt_token"], document_response.json()["id"], description
            )
          if document_response.status_code == 200 and update_response.status_code == 200:
              st.write("Successfully uploaded document.")
          else:
              st.write("Failed to upload document.")
              st.write(document_response.status_code)
              st.write(document_response)


def list_documents_to_delete(request_manager):
    st.write("---")
    st.title("Documents Uploaded")
    document_response = request_manager.get_document_list(st.session_state["jwt_token"])
    if document_response.status_code == 200:
        documents = document_response.json()
        checkboxes = {}
        for idx, doc in enumerate(documents):
            col_1, col_2 = st.columns([1, 16])
            checkboxes[idx] = col_1.checkbox("", key=idx)
            col_2.write("__Name:__ " +doc["title"])
            st.code("Description: " +doc["description"])
            st.divider()
        if st.button("Delete selected"):
            for idx, doc in enumerate(documents):
                if checkboxes[idx]:
                    delete_response = request_manager.delete_document(
                        st.session_state["jwt_token"], doc["id"]
                    )
                    if delete_response.status_code == 200:
                        st.write("Successfully deleted document.")
                    else:
                        st.write("Failed to delete document.")
                        st.write(delete_response.status_code)
                        st.write(delete_response)
            st.rerun()


def handle_document_display(request_manager):
    upload_document(request_manager)
    list_documents_to_delete(request_manager)


def main():
    session_login_wrapper(handle_document_display)


if __name__ == "__main__":
    main()
