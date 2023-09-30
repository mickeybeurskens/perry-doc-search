import streamlit as st
from perry.requests import RequestManager
from perry.authentication import session_login_wrapper


def handle_conversation_selection(request_manager: RequestManager):
    conversation_id = None
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
        if conversation_id:
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
    return conversation_id


def display_conversation_info(conversation_info):
    st.sidebar.write("__Agent Type:__ ", conversation_info["agent_type"])
    st.sidebar.write("__Agent Settings:__", conversation_info["agent_settings"])
    st.sidebar.write("__Documents:__")
    if len(conversation_info["doc_titles"]) == 0:
        st.sidebar.info("- No documents")
    else:
        st.sidebar.write([doc_title for doc_title in conversation_info["doc_titles"]])


def show_chat(request_manager: RequestManager, conversation_id: int):
    st.session_state["messages"] = [
        {"user": "user", "message": "Hello!", "timestamp": "2021-08-01 12:00:00"},
        {"user": "assistant", "message": "Hi there!", "timestamp": "2021-08-01 12:00:01"},
    ]
    for message in st.session_state["messages"]:
        with st.chat_message(message["user"]):
            st.write(message["message"])

    message = st.chat_input("Chat with Perry", key="message")
    if message:
        st.session_state["messages"].append(
            {"user": "user", "message": message, "timestamp": "2021-08-01 12:00:02"}
        )
        agent_response = request_manager.query_agent(
            st.session_state["jwt_token"], conversation_id, message
        )
        if agent_response.status_code == 200:
            agent_response = agent_response.json()
            st.session_state["messages"].append(
                {
                    "user": "assistant",
                    "message": agent_response["response"],
                    "timestamp": agent_response["timestamp"],
                }
            )
        st.rerun()
            
    


def handle_user_display(request_manager):
    conversation_id = handle_conversation_selection(request_manager)
    show_chat(request_manager, conversation_id)


def main():
    st.set_page_config(page_title="Chat")
    session_login_wrapper(handle_user_display)


if __name__ == "__main__":
    main()
