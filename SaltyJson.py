import requests
import time
class SaltyJson():
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()

    def get_json(self):
        try:
            self.response = self.session.get(self.url, headers={"User-Agent": "Mozilla/5.0", "Accept":"application/json"})
            if self.response.status_code != 200:
                print(self.response.status_code)
                print(self.response.json())
                self.get_json()       
            else:
                return self.response.json()                
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            self.get_json()
        except requests.exceptions.JSONDecodeError:
            time.sleep(1)
            self.get_json()