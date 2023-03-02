import requests

class SaltyJson():
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()

    def get_json(self):
        try:
            self.response = self.session.get(self.url, headers={"User-Agent": "Mozilla/5.0"})
            if self.response.status_code != 200:
                self.get_json()       
            else:
                return self.response.json()                
        except requests.exceptions.ConnectionError:
            self.get_json()
        except requests.exceptions.JSONDecodeError:
            self.get_json()


