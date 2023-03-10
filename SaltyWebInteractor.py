import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
import time

load_dotenv()

URL_SIGNIN = 'https://www.saltybet.com/authenticate?signin=1'
URL_BET = 'https://www.saltybet.com/ajax_place_bet.php'


class SaltyWebInteractor():
    def __init__(self):
        self.session = requests.session()
        self.login()

    def check_env_variables(self):
        dotenv_path = find_dotenv()
        if dotenv_path:
            return True
        else:       
            return False

    def login(self):
        self.session.get(URL_SIGNIN)
        if self.check_env_variables():
            try:
                login_data = {'email': os.getenv('email'), 'pword': os.getenv('password'), 'authenticate': 'signin'}
                self.session.post(URL_SIGNIN, data=login_data)
            except:
                print("Login failed.")
            else:
                print("Login success!")
        else:
            print("Unable to login due to missing .env file.  Please see README for setup instructions.")

    def refresh_session(self):
        response = self.session.get('https://www.saltybet.com/')
        return response

    def get_balance(self):
        try:
            bal_req = self.refresh_session()
            soup_parser = BeautifulSoup(bal_req.content, "html.parser")
            balance = int(soup_parser.find(id="balance").string.replace(',', ''))
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
