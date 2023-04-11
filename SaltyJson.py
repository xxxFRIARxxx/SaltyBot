import requests
import time
import json
class SaltyJson():
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0", "Accept":"application/json"})

    def get_json(self):
        try:
            self.response = self.session.get(self.url)
            if self.response.status_code != 200:
                print(f"Received {self.response.status_code} status code, retrying... ")
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

    def json_is_valid(self, json_data):
        try:
            required_keys = ["p1name", "p2name", "p1total", "p2total", "status", "alert", "remaining"]

            for key in required_keys:
                if key in json_data and json_data[key]:
                    return True
                print(f"Invalid data: key '{key}' is missing or has a falsey value")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

