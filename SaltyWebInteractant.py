import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time

load_dotenv()

URL_SIGNIN = 'https://www.saltybet.com/authenticate?signin=1'
URL_BET = 'https://www.saltybet.com/ajax_place_bet.php'

cookies = {
    '_ga': 'GA1.2.410504609.1668662511',
    '_gid': 'GA1.2.1665887669.1675437246',
    'PHPSESSID': '6ucnbid62ogacdm504l7chioq0',
}

headers = {
    'authority': 'www.saltybet.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': '_ga=GA1.2.410504609.1668662511; _gid=GA1.2.1665887669.1675437246; PHPSESSID=6ucnbid62ogacdm504l7chioq0',
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

class SaltyWebInteractant():
    def __init__(self):
        self.session = requests.session()
        self.login()

    def login(self):
        login_data = {'email': os.getenv('EMAIL'), 'pword': os.getenv('PASSWORD'), 'authenticate': 'signin'}
        response = self.session.post(URL_SIGNIN, data=login_data)
        if ( response.url != "https://www.saltybet.com/" and response.url != "http://www.saltybet.com/" ):
            raise RuntimeError("Error: Wrong URL: " + response.url)

    def refresh_session(self):
        response = requests.get('https://www.saltybet.com/', cookies=cookies, headers=headers)
        return response

    def get_balance(self):
        try:
            response = requests.get('https://www.saltybet.com/', cookies=cookies, headers=headers)
            soup_parser = BeautifulSoup(response.content, "html.parser")
            balance = int(soup_parser.find(id="balance").string.replace(',',''))
            return balance
        except requests.exceptions.HTTPError:
            time.sleep(2)
            self.login()
            self.get_balance()
        except requests.exceptions.SSLError:
            time.sleep(2)
            self.login()
            self.get_balance()

    def place_bet_on_website(self, bet_data):
        self.session.post(URL_BET, cookies = cookies, headers = headers, data = bet_data)
        print("Bet placed of $" + str(bet_data['wager']) + " on " + str(bet_data['selectedplayer']))


