import streamlit as st
from perry.requests import RequestManager
from perry.authentication import session_login_wrapper


def handle_conversation_selection(request_manager):
    st.sidebar.header("Select Conversation")
    conversation_response = request_manager.get_conversations(
        st.session_state["jwt_token"]
    )
    if conversation_response.status_code == 200:
        conversation_info = conversation_response.json()
        conversation_ids = [conversation["id"] for conversation in conversation_info]
        conversation_id = st.sidebar.selectbox(
            "Select a conversation", conversation_ids
        )
        if conversation_id:
            display_conversation_info(conversation_info[conversation_id])
    else:
        st.write("Failed to retrieve conversations.")
        st.write(conversation_info.status_code)
        st.write(conversation_info.json())
    st.sidebar.write("---")


def display_conversation_info(conversation_info):
    st.write(conversation_info)


def handle_user_display(request_manager):
    handle_conversation_selection(request_manager)


def main():
    st.set_page_config(page_title="Chat")
    session_login_wrapper(handle_user_display)


if __name__ == "__main__":
    main()
