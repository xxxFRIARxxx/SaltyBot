import requests
import time


class SaltyJson():
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Accept": "application/json"})

    def get_json(self):
        try:
            self.response = self.session.get(self.url)

            if self.response.status_code != 200:
                print("status code received:", self.response.status_code)
                time.sleep(1)
                self.get_json()
            else:
                if not self.response.text:
                    # blank / empty response recieved
                    print("received empty response from server, retrying...")
                    print("response.text:", self.response.text)
                    print("response.content:", self.response.content)
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
