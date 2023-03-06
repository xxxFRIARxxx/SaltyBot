import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time

load_dotenv()

URL_SIGNIN = 'https://www.saltybet.com/authenticate?signin=1'
URL_BET = 'https://www.saltybet.com/ajax_place_bet.php'

headers = {
    'authority': 'www.saltybet.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

class SaltyWebInteractor():
    def __init__(self):
        self.session = requests.session()
        self.login()

    def login(self):
        self.session.get(URL_SIGNIN)
        login_data = {'email': os.getenv('email'), 'pword': os.getenv('password'), 'authenticate': 'signin'}
        response = self.session.post(URL_SIGNIN, data=login_data)

        if ( response.url != "https://www.saltybet.com/" and response.url != "http://www.saltybet.com/" ):
            raise RuntimeError("Error: Wrong URL: " + response.url)

    def refresh_session(self):
        response = requests.get('https://www.saltybet.com/', cookies = self.session.cookies)
        return response

    def get_balance(self):
        try:
            r = requests.get('https://www.saltybet.com/', cookies = self.session.cookies)
            soup_parser = BeautifulSoup(r.content, "html.parser")
            balance = int(soup_parser.find(id="balance").string.replace(',',''))
            return balance
        except requests.exceptions.HTTPError:
            time.sleep(.25)
            self.login()
            self.get_balance()
        except requests.exceptions.SSLError:
            time.sleep(.25)
            self.login()
            self.get_balance()
        except requests.exceptions.ConnectionError:
            time.sleep(.25)
            self.login()
            self.get_balance()

    def place_bet_on_website(self, bet_data):
        try:
            self.session.post(URL_BET, data = bet_data, cookies=self.session.cookies)
            print(f"Bet placed: ${bet_data['wager']:,} on {bet_data['selectedplayer']}")
        except requests.exceptions.ConnectionError:
            time.sleep(.25)
            self.login()
            self.place_bet_on_website()



