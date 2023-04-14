import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
import time
from tenacity import retry, retry_if_result, stop_after_attempt, wait_fixed

load_dotenv()

URL_SIGNIN = 'https://www.saltybet.com/authenticate?signin=1'
URL_BET = 'https://www.saltybet.com/ajax_place_bet.php'

class SaltyWebInteractor():
    def __init__(self):
        self.session = requests.session()
        self.login()

    def login(self):
        self.session.get(URL_SIGNIN)
        if find_dotenv():
            try:
                login_data = {'email': os.getenv('email'), 'pword': os.getenv('password'), 'authenticate': 'signin'}
                response = self.session.post(URL_SIGNIN, data=login_data)
                if response.url == "https://www.saltybet.com/":
                    print("Login successful!")
                elif response.url == "https://www.saltybet.com/authenticate?signin=1&error=Invalid%20Email%20or%20Password":
                    print("Login failed. Invalid email or password.")
                else:
                    print("Unknown redirect URL:", response.url)
            except requests.exceptions.RequestException as e:
                print("Failed to login to SaltyBet:", e)
        else:
            print("Unable to login due to missing .env file.  Please see README for setup instructions.")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), retry_error_callback=lambda x: x.status_code != 200)
    def refresh_session(self):
        response = self.session.get('https://www.saltybet.com/')
        response.raise_for_status()
        return response

    @retry(retry=retry_if_result(lambda result: not result), stop=stop_after_attempt(3), wait=wait_fixed(0.25))
    def get_balance(self):
        try:
            bal_req = self.refresh_session()
            soup_parser = BeautifulSoup(bal_req.content, "html.parser")
            balance = int(soup_parser.find(id="balance").string.replace(',', ''))
        except (requests.exceptions.HTTPError, requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            self.login()
            return None
        else:
            return balance

    def place_bet_on_website(self, bet_data):
        try:
            self.session.post(URL_BET, data=bet_data)
            print(f"Bet placed: ${bet_data['wager']:,} on {bet_data['selectedplayer']}")
        except requests.exceptions.ConnectionError:
            time.sleep(.25)
            self.login()
            self.place_bet_on_website()