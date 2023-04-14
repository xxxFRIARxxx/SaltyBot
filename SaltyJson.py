import requests
import time
import json

from tenacity import retry, stop_after_attempt, wait_fixed, RetryError


class SaltyJson:
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "application/json"})

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(1),
           retry_error_callback=lambda r: print(f"Error: {r}"))
    def get_json(self):
        self.response = self.session.get(self.url)
        if self.response.status_code != 200:
            print(f"Received {self.response.status_code} status code, retrying... ")
            raise requests.exceptions.ConnectionError
        elif not self.response.text:
            print("Blank response received, retrying...")
            raise RetryError
        elif self.json_is_valid(self.response.json()) is True:
            return self.response.json()
        else:
            raise RetryError

    def json_is_valid(self, json_data):
        try:
            required_keys = ["p1name", "p2name", "p1total", "p2total", "status", "remaining"]

            for key in required_keys:
                if key in json_data and json_data[key]:
                    return True
                print(f"Invalid data: key '{key}' is missing or has a falsey value")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False
