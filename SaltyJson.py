import requests

class SaltyJson():
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()

    def get_json(self):
        self.response = self.session.get(self.url, headers={"User-Agent": "Mozilla/5.0"})
        return self.response.json()