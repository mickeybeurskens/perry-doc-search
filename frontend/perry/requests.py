import requests


class RequestManager:
    def __init__(self, base_url):
        self.base_url = base_url

    def register(self, username, password):
        response = requests.post(
            f"{self.base_url}/users/register",
            json={"username": username, "password": password},
        )
        return response

    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/users/token/",
            data={"username": username, "password": password},
        )
        return response

    def get_user_info(self, token):
        response = requests.get(
            f"{self.base_url}/users/info", headers=self._get_auth_header(token)
        )
        return response

    def get_conversations(self, token):
        response = requests.get(
            f"{self.base_url}/conversations/", headers=self._get_auth_header(token)
        )
        return response

    def get_document_list(self, token):
        response = requests.get(
            f"{self.base_url}/documents/info/", headers=self._get_auth_header(token)
        )
        return response

    def upload_document(self, token, document):
        response = requests.post(
            f"{self.base_url}/documents/file/",
            headers=self._get_auth_header(token),
            files={"file": (document.name, document.read(), "application/pdf")},
        )
        return response

    def update_document(self, token, document_id, title, description):
        response = requests.put(
            f"{self.base_url}/documents/info/{document_id}",
            headers=self._get_auth_header(token),
            json={"description": description, "title": title, "id": document_id},
        )
        return response

    def delete_document(self, token, document_id):
        response = requests.delete(
            f"{self.base_url}/documents/file/{document_id}",
            headers=self._get_auth_header(token),
        )
        return response

    def _get_auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}
