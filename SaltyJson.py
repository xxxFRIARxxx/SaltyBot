import requests

class SaltyJson():
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()

    def get_json(self):
        try:
            self.response = self.session.get(self.url, headers={"User-Agent": "Mozilla/5.0"})
            return self.response.json()
        except requests.exceptions.ConnectionError:
            self.session = requests.Session()
            self.get_json()
        except requests.exceptions.JSONDecodeError:
            self.session = requests.Session()
            self.get_json()
