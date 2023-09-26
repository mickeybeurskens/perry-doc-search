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
            f"{self.base_url}/users/token",
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
            f"{self.base_url}/conversations", headers=self._get_auth_header(token)
        )
        return response

    def _get_auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}