import requests
import time
class SaltyJson():
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0", "Accept":"application/json"})

    def get_json(self):
        try:
            self.response = self.session.get(self.url)
            if self.response.status_code != 200:
                print("Received non-200 status code, retrying... ")
                print(self.response.status_code)
                time.sleep(1)
                return self.get_json()
            elif not self.response.text:
                print("Blank response receieved, retrying...")
                time.sleep(1)
                return self.get_json()
            else:
                return self.response.json()
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            return self.get_json()
        except requests.exceptions.JSONDecodeError:
            print("Error Decoding JSON, retrying...")
            time.sleep(1)
            return self.get_json()