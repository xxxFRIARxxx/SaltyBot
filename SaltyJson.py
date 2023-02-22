import requests

class SaltyJson():
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()

    def get_json(self):
        self.response = self.session.get(self.url, headers={"User-Agent": "Mozilla/5.0"})
        self.response.raise_for_status()
        if self.response.status_code != 204:
            return self.response.json()