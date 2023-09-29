import streamlit as st
from perry.requests import RequestManager
from perry.authentication import session_login_wrapper


def handle_conversation_selection(request_manager: RequestManager):
    st.sidebar.header("Select Conversation")
    conversation_response = request_manager.get_conversations(
        st.session_state["jwt_token"]
    )
    if conversation_response.status_code == 200:
        conversation_info = conversation_response.json()
        conversation_id = st.sidebar.selectbox(
            "Select a conversation",
            [
                str(conversation["id"]) + ": " + conversation["name"]
                for conversation in conversation_info
            ],
        )
        conversation_id = int(conversation_id.split(":")[0])
        conversation = [
            conversation
            for conversation in conversation_info
            if conversation["id"] == conversation_id
        ][0]
        if conversation:
            display_conversation_info(conversation)
    else:
        st.write("Failed to retrieve conversations.")
        st.write(conversation_info.status_code)
        st.write(conversation_info.json())
    st.sidebar.write("---")


def display_conversation_info(conversation_info):
    st.write(conversation_info)
    # st.sidebar.write("__Agent Type:__ ", conversation_info["agent_type"])
    st.sidebar.write("__Agent Settings:__", conversation_info["agent_settings"])
    st.sidebar.write("__Documents:__")
    if len(conversation_info["doc_titles"]) == 0:
        st.sidebar.info("- No documents")
    else:
        for doc_title in conversation_info["doc_titles"]:
            st.sidebar.info("-", doc_title)


def handle_user_display(request_manager):
    handle_conversation_selection(request_manager)


def main():
    st.set_page_config(page_title="Chat")
    session_login_wrapper(handle_user_display)


if __name__ == "__main__":
    main()
