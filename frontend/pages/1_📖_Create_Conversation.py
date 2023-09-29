import streamlit as st
import pandas as pd
from perry.requests import RequestManager
from perry.authentication import session_login_wrapper


def get_selected_document_ids(request_manager: RequestManager):
    st.subheader("Select documents to add to conversation:")
    document_response = request_manager.get_document_list(st.session_state["jwt_token"])
    if document_response.status_code != 200:
        st.write("Failed to get documents.")
        st.write("Response status code: " + str(document_response.status_code))
        st.write("Response: " + str(document_response.json()))
        return
    
    documents = document_response.json()
    selected_document_ids = []
    for idx, doc in enumerate(documents):
        if st.checkbox(doc["title"], key=idx):
            selected_document_ids.append(doc["id"])
    return selected_document_ids


def select_agent_type_with_settings(request_manager: RequestManager):
    agent_info_response = request_manager.get_agent_registry_info(
        st.session_state["jwt_token"]
    )
    type_and_settings = {"type": None, "settings": None}
    if agent_info_response.status_code == 200:
        info = agent_info_response.json()
        # Select one agent type
        agent_type = st.selectbox("Select an agent type:", [i["name"] for i in info])

        # Get settings schema for selected agent type
        settings_schema = None
        for i in info:
            if i["name"] == agent_type:
                settings_schema = i["settings_schema"]
                break
        if settings_schema is None:
            st.write("Failed to get agent settings schema.")
            return
        st.write(settings_schema)
        # Get settings for selected agent type
        agent_settings = {}
        for key, value in settings_schema.items():
            title = value["title"]
            if value["type"] == "integer" or value["type"] == "number":
                agent_settings[key] = st.number_input(title)
            elif value["type"] == "boolean":
                agent_settings[key] = st.checkbox(title)
            else:
                agent_settings[key] = st.text_input(title)
        type_and_settings["type"] = agent_type
        type_and_settings["settings"] = agent_settings
    else:
        st.write("Failed to get agent info.")
        st.write("Response status code: " + str(agent_info_response.status_code))
        st.write("Response: " + str(agent_info_response.json()))
    return type_and_settings


def create_new_conversation(request_manager: RequestManager, document_ids, agent_type, agent_settings):
    name = st.text_input("Enter a name for the conversation.")
    if name == "" or name == " ":
        name = None
    if name:
        button_press = st.button("Create")
        if button_press:
            create_response = request_manager.create_conversation(
                st.session_state["jwt_token"], name, agent_type, agent_settings, document_ids
            )
            if create_response.status_code == 201:
                st.write("Successfully created conversation.")
            else:
                st.write("Failed to create conversation.")
                st.write(create_response.status_code)
                st.write(create_response.json())


def create_conversation(request_manager: RequestManager):
    st.title("Create New Conversation")
    document_ids = get_selected_document_ids(request_manager)
    st.info("Selected document IDs: " + str(document_ids))
    agent_type_and_settings = select_agent_type_with_settings(request_manager)
    st.info(agent_type_and_settings)
    if agent_type_and_settings["type"] and agent_type_and_settings["settings"]:
        create_new_conversation(
            request_manager,
            document_ids,
            agent_type_and_settings["type"],
            agent_type_and_settings["settings"],
        )


def list_conversations(request_manager: RequestManager):
    st.title("Overview")
    conversation_response = request_manager.get_conversations(
        st.session_state["jwt_token"]
    )
    if conversation_response.status_code == 200:
        conversations = conversation_response.json()
        if not conversations:
            st.info("No conversations found.")
            return
        for conversation in conversations:
            st.write("__Name:__ " + conversation["name"])
            st.info("Description: " + conversation["description"])
            st.divider()
    else:
        st.write("Failed to get conversations.")
        st.write(conversation_response.status_code)
        st.write(conversation_response)


def handle_session(request_manager):
    create_conversation(request_manager)
    # list_conversations(request_manager)


def main():
    session_login_wrapper(handle_session)


if __name__ == "__main__":
    main()
