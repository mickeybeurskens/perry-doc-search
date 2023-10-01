import streamlit as st
from datetime import datetime
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
            if "conversation_id" not in st.session_state:
                st.session_state["conversation_id"] = conversation_id
            if st.session_state["conversation_id"] != conversation_id:
                st.session_state["messages"] = []
                st.session_state["conversation_id"] = conversation_id
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
        st.write(conversation_response.status_code)
        st.write(conversation_response.json())
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


def load_message_history(request_manager: RequestManager, conversation_id: int):
    message_history = request_manager.get_message_history(
        st.session_state["jwt_token"], conversation_id
    )
    processed_messages = []
    if message_history.status_code == 200:
        if not message_history.json():
            return []
        for messages in message_history.json():
            processed_message = {}
            processed_message["user"] = messages["role"]
            processed_message["message"] = messages["message"]
            processed_message["timestamp"] = datetime.strptime(
                messages["timestamp"], "%Y-%m-%dT%H:%M:%S.%f"
            )
            processed_messages.append(processed_message)
    else:
        st.write("Failed to retrieve message history.")
        st.write(message_history.status_code)
        st.write(message_history.json())
    return processed_messages


def show_chat(request_manager: RequestManager, conversation_id: int):
    if "messages" not in st.session_state:
        st.session_state["messages"] = load_message_history(
            request_manager, conversation_id
        )
    if st.session_state["messages"] is None:
        st.session_state["messages"] = load_message_history(
            request_manager, conversation_id
        )
    elif len(st.session_state["messages"]) == 0:
        st.session_state["messages"] = load_message_history(
            request_manager, conversation_id
        )

    for message in st.session_state["messages"]:
        with st.chat_message(message["user"]):
            st.write(message["message"])

    query = st.chat_input("Chat with Perry", key="query")

    if query:
        user_message = {
            "user": "user",
            "message": query,
            "timestamp": datetime.now(),
        }
        st.session_state["messages"].append(user_message)
        with st.chat_message(user_message["user"]):
            st.write(user_message["message"])

        with st.spinner("Writing response..."):
            agent_response = request_manager.query_agent(
                st.session_state["jwt_token"], conversation_id, query
            )
            if agent_response.status_code == 200:
                agent_response = agent_response.json()
                st.write(agent_response)
                st.session_state["messages"].append(
                    {
                        "user": "assistant",
                        "message": agent_response,
                        "timestamp": datetime.now(),
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
