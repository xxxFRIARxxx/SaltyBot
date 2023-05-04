import requests
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, TryAgain
from requests_cache import CachedSession


class SaltyJson:
    def __init__(self):
        self.url = "https://www.saltybet.com/state.json"
        self.session = self.create_session()

    def create_session(self):
        session = CachedSession('demo_cache', cache_control=True)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
        session.headers.update(headers)
        return session

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=2, max=8, jitter=1),
           retry_error_callback=lambda r: print(f"Error: {r}"))
    def get_json(self):
        response = self.session.get(self.url)
        return self.handle_response(response)

    def handle_response(self, response):
        if response.status_code != 200:
            print(f"Received {response.status_code} status code, retrying... ")
            raise requests.exceptions.ConnectionError
        elif response.text:
            return response.json()
        else:
            self.session.cache.clear()
            raise TryAgain