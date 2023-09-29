import requests


class RequestManager:
    def __init__(self, base_url):
        self.base_url = base_url

    def register(self, username, password):
        return requests.post(
            f"{self.base_url}/users/register",
            json={"username": username, "password": password},
        )

    def login(self, username, password):
        return requests.post(
            f"{self.base_url}/users/token/",
            data={"username": username, "password": password},
        )

    def get_user_info(self, token):
        return requests.get(
            f"{self.base_url}/users/info", headers=self._get_auth_header(token)
        )

    def get_conversations(self, token):
        return requests.get(
            f"{self.base_url}/conversations/", headers=self._get_auth_header(token)
        )
    
    def get_agent_registry_info(self, token):
        return requests.get(
            f"{self.base_url}/agents/info", headers=self._get_auth_header(token)
        )
    
    def create_conversation(self, token, name, agent_type, agent_settings, doc_ids):
        import streamlit as st

        assert isinstance(doc_ids, list)
        assert isinstance(agent_settings, dict)
        assert isinstance(name, str)
        assert isinstance(agent_type, str)
        if doc_ids:
            assert [isinstance(doc_id, int) for doc_id in doc_ids]

        json = {
            "name": name,
            "agent_type": agent_type,
            "agent_settings": agent_settings,
            "doc_ids": doc_ids,
        }
        st.write(json)
        return requests.post(
            f"{self.base_url}/conversations/",
            headers=self._get_auth_header(token),
            json=json
        )

    def get_document_list(self, token):
        return requests.get(
            f"{self.base_url}/documents/info/", headers=self._get_auth_header(token)
        )

    def upload_document(self, token, document):
        return requests.post(
            f"{self.base_url}/documents/file/",
            headers=self._get_auth_header(token),
            files={"file": (document.name, document.read(), "application/pdf")},
        )

    def update_document(self, token, document_id, title, description):
        return requests.put(
            f"{self.base_url}/documents/info/{document_id}",
            headers=self._get_auth_header(token),
            json={"description": description, "title": title, "id": document_id},
        )
        
    def delete_document(self, token, document_id):
        return requests.delete(
            f"{self.base_url}/documents/file/{document_id}",
            headers=self._get_auth_header(token),
        )

    def _get_auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}
