import streamlit as st
import pandas as pd
from perry.requests import RequestManager
from perry.authentication import session_login_wrapper


def get_selected_document_ids(request_manager: RequestManager):
    st.subheader("Select documents")
    document_response = request_manager.get_document_list(st.session_state["jwt_token"])
    if document_response.status_code != 200:
        st.write("Failed to get documents.")
        st.write("Response status code: " + str(document_response.status_code))
        st.write("Response: " + str(document_response.json()))
        return

    documents = document_response.json()
    if len(documents) == 0:
        st.info("No documents found.")
    selected_document_ids = []
    for idx, doc in enumerate(documents):
        if st.checkbox(doc["title"], key=idx):
            selected_document_ids.append(doc["id"])
    return selected_document_ids


def get_agent_settings_from_user(settings_schema):
    agent_settings = {}
    for key, value in settings_schema.items():
        title = value["title"]
        if value["type"] == "integer" or value["type"] == "number":
            if "maximum" in value.keys() and "minimum" in value.keys():
                agent_settings[key] = st.number_input(
                    title, min_value=value["minimum"], max_value=value["maximum"]
                )
            elif "minimum" in value.keys():
                agent_settings[key] = st.number_input(title, min_value=value["minimum"])
            elif "maximum" in value.keys():
                agent_settings[key] = st.number_input(title, max_value=value["maximum"])
            else:
                agent_settings[key] = st.number_input(title)
        elif value["type"] == "boolean":
            agent_settings[key] = st.checkbox(title)
        else:
            if "choices" in value.keys():
                agent_settings[key] = st.selectbox(title, value["choices"])
            else:
                agent_settings[key] = st.text_input(title)
    return agent_settings


def show_agent_variable_settings(info):
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

    # Get settings for selected agent type
    agent_settings = get_agent_settings_from_user(settings_schema)
    
    type_and_settings = {}
    type_and_settings["type"] = agent_type
    type_and_settings["settings"] = agent_settings
    return type_and_settings


def select_agent_type_with_settings(request_manager: RequestManager):
    st.subheader("Select agent type and settings")
    agent_info_response = request_manager.get_agent_registry_info(
        st.session_state["jwt_token"]
    )
    type_and_settings = {"type": None, "settings": None}
    if agent_info_response.status_code == 200:
        info = agent_info_response.json()
        type_and_settings = show_agent_variable_settings(info)
    else:
        st.warning("Failed to get agent info.")
        st.warning("Response status code: " + str(agent_info_response.status_code))
        st.warning("Response: " + str(agent_info_response.json()))
    return type_and_settings


def create_new_conversation(
    request_manager: RequestManager, document_ids, agent_type, agent_settings
):
    name = st.text_input("Enter a name for the conversation.")
    button_press = st.button("Create")
    if name == "" or name == " ":
        name = None
    if not name and button_press:
        st.warning("Please enter a name for the conversation.")
    if name:
        if button_press:
            create_response = request_manager.create_conversation(
                st.session_state["jwt_token"],
                name,
                agent_type,
                agent_settings,
                document_ids,
            )
            if create_response.status_code == 201:
                st.info("Successfully created conversation.")
            else:
                st.warning("Failed to create conversation.")
                st.warning(create_response.status_code)
                st.warning(create_response.json())


def create_conversation(request_manager: RequestManager):
    st.title("Create New Conversation")
    document_ids = get_selected_document_ids(request_manager)
    st.divider()
    agent_type_and_settings = select_agent_type_with_settings(request_manager)
    if agent_type_and_settings["type"] and agent_type_and_settings["settings"]:
        create_new_conversation(
            request_manager,
            document_ids,
            agent_type_and_settings["type"],
            agent_type_and_settings["settings"],
        )


def list_conversations_with_delete_checkbox(request_manager: RequestManager):
    st.title("Overview")
    conversation_response = request_manager.get_conversations(
        st.session_state["jwt_token"]
    )
    delete_conv = {}
    delete_button = st.button("Delete selected conversations")

    if conversation_response.status_code == 200:
        conversations = conversation_response.json()
        if not conversations:
            st.info("No conversations found.")
            return
        for conversation in conversations:
            st.subheader(conversation["name"])
            # st.write(conversation)
            col_1, col_2 = st.columns([1, 35])
            delete_conv[conversation["id"]] = col_1.checkbox("", key=conversation["id"])
            col_2.write("__ID:__ " + str(conversation["id"]))
            # st.write("Agent type: " + str(conversation["agent_type"]))
            st.write("__Agent settings:__ " + str(conversation["agent_settings"]))
            st.write("__Documents__: " + str(conversation["doc_titles"]))
            st.divider()
    else:
        st.write("Failed to get conversations.")
        st.write(conversation_response.status_code)
        st.write(conversation_response)
    
    if delete_button:
        for del_id in delete_conv.keys():
            if delete_conv[del_id]:
                delete_response = request_manager.delete_conversation(
                    st.session_state["jwt_token"], del_id
                )
                if not delete_response.status_code == 204:
                    st.warning("Failed to delete conversation.")
                    st.warning(delete_response.status_code)
                    st.warning(delete_response.json())
        st.rerun()



def handle_session(request_manager):
    create_conversation(request_manager)
    list_conversations_with_delete_checkbox(request_manager)


def main():
    session_login_wrapper(handle_session)


if __name__ == "__main__":
    main()
