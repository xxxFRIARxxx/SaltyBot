import requests
import time


class SaltyJson():
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        self.session.timeout = 5

    def get_json(self):
        try:
            self.response = self.session.get(self.url)

            if self.response.status_code != 200:
                self.get_json()
            else:
                if len(self.response.text) == 0:
                    # blank / empty response recieved
                    time.sleep(1)
                    self.get_json()
                else:
                    return self.response.json()
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            self.get_json()
        except requests.exceptions.JSONDecodeError:
            time.sleep(1)
            self.get_json()
