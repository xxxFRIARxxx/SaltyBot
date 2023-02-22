import requests
import os
from SaltyJson import SaltyJson
from SaltyParser import SaltyJsonParser
from SaltyDatabase import SaltyRecorder
from SaltySocket import SaltySocket
from SaltyTimer import SaltyTimer
from SaltyWebInteractant import SaltyWebInteractant
from SaltyBettor import SaltyBettor

clear = lambda: os.system('cls')

json_url = "https://www.saltybet.com/state.json"
session_obj = requests.Session()
response = session_obj.get(json_url, headers={"User-Agent": "Mozilla/5.0"})
jsoninfo = response.json()

new_match = 0
match_start_time = 0
total_match_time_sec = 0

my_thing = SaltyJson()
recorder = SaltyRecorder()
my_socket = SaltySocket()
gameTime = SaltyTimer()
bettor = SaltyBettor()
interactor = SaltyWebInteractant()

my_socket.open_socket()
my_socket.send_ping()

first_run = True
previousGameMode = None
gameStateLies = False
previousGameState = None

while True:
    the_json = my_thing.get_json()
    my_parser = SaltyJsonParser(the_json)
    balance = interactor.get_balance()
    
    gameMode = my_parser.get_gameMode()
    if (gameMode != previousGameMode):
        gameStateLies = True
    previousGameMode = gameMode
    
    gameState = my_parser.get_gamestate()
    if (gameState != previousGameState):
        gameStateLies = False
    previousGameState = gameState
    
    # TODO: SaltySocket should call readmessag here
    if ((gameMode != 'Exhibition') and (gameStateLies == False)):
        if (gameState == 'open'):
            if (new_match == 0):
                first_run = False
                bettor.set_balance(balance) # Sets and displays current balance of your account.
                p1DB_ratings = bettor.get_player_rating(recorder.get_ratings_from_DB(my_parser.get_p1name())) # Gets Mu and Sigma for Player 1 in DB, sets them to default if there are no prior matches in the DB, and sets them accordingly if there are. # TODO: Put these variables in more global scope (up above before the while loop)
                p2DB_ratings = bettor.get_player_rating(recorder.get_ratings_from_DB(my_parser.get_p2name())) # Gets Mu and Sigma for Player 2 in DB, sets them to default if there are no prior matches in the DB, and sets them accordingly if there are.
                # TODO:  Eventually do something with the Mu and Sigma (and regression of data) to compose bet, and place it below:
                interactor.place_bet_on_website(bettor.format_bet(gameMode, my_parser.get_p1name(), my_parser.get_p2name())) # Decide bet, and place bet 
                new_match = 1
                my_socket.find_winstreak = True
                print(f"Player 1 Rating:   Mu = {p1DB_ratings.mu}  Sigma = {p1DB_ratings.sigma}")
                print(f"Player 2 Rating:   Mu = {p2DB_ratings.mu}  Sigma = {p2DB_ratings.sigma}")
                my_socket.get_tier() # NOTE: Can come back None.  Not encouraged.  Passes through.
        elif (gameState == 'locked'):
            if (first_run == False):
                if (new_match == 1):
                    new_match = 2
                    gameTime.timer_start()
                    my_socket.get_winstreaks()  # NOTE: Can come back None.  Encouraged.  If so, sets winstreaks to None.
                    print(f'Winstreaks are: {my_socket.p1winstreak, my_socket.p2winstreak}')
        elif (gameState == '1') or ((gameState == '2')): 
            if (first_run == False):
                if (new_match == 2):
                    new_match = 0
                    gameTime.timer_snapshot()
                    ratings_to_db = bettor.update_ranking_after(gameState, p1DB_ratings, p2DB_ratings) # Updates ratings after the match.
                    my_socket.adjust_winstreak(my_parser.set_p1winstatus(), my_parser.set_p2winstatus())
                    bettor.bet_outcome(my_parser.get_p1name(), my_parser.get_p2name(), gameState)
                    recorder.record_match(my_parser.get_p1name(),my_parser.get_p1odds(), my_parser.set_p1winstatus(), my_parser.get_p2name(), my_parser.get_p2odds(), my_parser.set_p2winstatus(), my_socket.adj_p1winstreak, my_socket.adj_p2winstreak, ratings_to_db[0].mu, ratings_to_db[0].sigma, ratings_to_db[1].mu, ratings_to_db[1].sigma, gameTime.snapshot, bettor.outcome, my_socket.tier_res_conv, my_parser.is_tourney())
    else:
        print ("In Exhibitions, nothing is recorded, and no bets are placed.")

# TODO: NEW EXPLOSION:
                # Traceback (most recent call last):
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\urllib3\connectionpool.py", line 703, in urlopen
                #     httplib_response = self._make_request(
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\urllib3\connectionpool.py", line 386, in _make_request
                #     self._validate_conn(conn)
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\urllib3\connectionpool.py", line 1042, in _validate_conn        
                #     conn.connect()
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\urllib3\connection.py", line 414, in connect
                #     self.sock = ssl_wrap_socket(
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\urllib3\util\ssl_.py", line 449, in ssl_wrap_socket
                #     ssl_sock = _ssl_wrap_socket_impl(
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\urllib3\util\ssl_.py", line 493, in _ssl_wrap_socket_impl       
                #     return ssl_context.wrap_socket(sock, server_hostname=server_hostname)
                #   File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.2800.0_x64__qbz5n2kfra8p0\lib\ssl.py", line 513, in wrap_socket
                #     return self.sslsocket_class._create(
                #   File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.2800.0_x64__qbz5n2kfra8p0\lib\ssl.py", line 1071, in _create
                #     self.do_handshake()
                #   File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.2800.0_x64__qbz5n2kfra8p0\lib\ssl.py", line 1342, in do_handshake
                #     self._sslobj.do_handshake()
                # ssl.SSLError: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:997)

                # During handling of the above exception, another exception occurred:

                # Traceback (most recent call last):
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\adapters.py", line 489, in send
                #     resp = conn.urlopen(
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\urllib3\connectionpool.py", line 787, in urlopen
                #     retries = retries.increment(
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\urllib3\util\retry.py", line 592, in increment
                #     raise MaxRetryError(_pool, url, error or ResponseError(cause))
                # urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='www.saltybet.com', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLError(1, '[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:997)')))

                # During handling of the above exception, another exception occurred:

                # Traceback (most recent call last):
                #   File "e:\Python Scripts\SaltyBot\SaltyStateMachine.py", line 40, in <module>
                #     balance = interactor.get_balance()
                #   File "e:\Python Scripts\SaltyBot\SaltyWebInteractant.py", line 50, in get_balance
                #     response = requests.get('https://www.saltybet.com/', cookies=cookies, headers=headers)
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\api.py", line 73, in get
                #     return request("get", url, params=params, **kwargs)
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\api.py", line 59, in request
                #     return session.request(method=method, url=url, **kwargs)
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\sessions.py", line 587, in request
                #     resp = self.send(prep, **send_kwargs)
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\sessions.py", line 701, in send
                #     r = adapter.send(request, **kwargs)
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\adapters.py", line 563, in send
                #     raise SSLError(e, request=request)
                # requests.exceptions.SSLError: HTTPSConnectionPool(host='www.saltybet.com', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLError(1, '[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failur failure (_ssl.c:997)')))


# TODO: Last match looks like:
                # Currently in Tournament with 0 matches remaining.  Game state is locked.
                # Currently in Tournament with 0 matches remaining.  Game state is locked.
                # Currently in Tournament with 0 matches remaining.  Game state is locked.
                # Currently in Exhibition with 25 matches remaining.  Game state is 1.
                # Nothing should be recorded in Exhibitions.
                # Currently in Exhibition with 25 matches remaining.  Game state is 1.
                # Nothing should be recorded in Exhibitions.
                # Currently in Exhibition with 25 matches remaining.  Game state is 1.
                # Nothing should be recorded in Exhibitions.
                # Currently in Exhibition with 25 matches remaining.  Game state is 1.


# TODO: Last match of exhib records as MM:
                # Nothing should be recorded in Exhibitions.
                # Currently in Exhibition with 2 matches remaining.  Game state is locked.
                # Nothing should be recorded in Exhibitions.
                # Currently in Matchmaking with 100 matches remaining.  Game state is 2.
                # Player 2 wins!
                # Player 1's new rating is trueskill.Rating(mu=33.506, sigma=4.889).  Player 2's new rating is trueskill.Rating(mu=38.643, sigma=4.906)
                # You lost the bet.
                # [('Beavis', 1.0, 0, -1, 33.50605031071917, 4.888723200212475, 'Butt-head', 1.6, 1, 4, 38.64297567161436, 4.906324626458675, 3982.0, 0, 0)]

# TODO  HANG - 0 MATCHES REMAINING (SB BROKE)
                # Currently in Matchmaking with 0 matches remaining.  Game state is open.
                # Currently in Matchmaking with 0 matches remaining.  Game state is open.
                # Currently in Matchmaking with 0 matches remaining.  Game state is open.

# TODO: EXPLOSION:
                # Traceback (most recent call last):
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\models.py", line 971, in json
                #     return complexjson.loads(self.text, **kwargs)
                #   File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.2800.0_x64__qbz5n2kfra8p0\lib\json\__init__.py", line 346, in loads
                #     return _default_decoder.decode(s)
                #   File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.2800.0_x64__qbz5n2kfra8p0\lib\json\decoder.py", line 337, in decode
                #     obj, end = self.raw_decode(s, idx=_w(s, 0).end())
                #   File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.2800.0_x64__qbz5n2kfra8p0\lib\json\decoder.py", line 355, in raw_decode
                #     raise JSONDecodeError("Expecting value", s, err.value) from None
                # json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

                # During handling of the above exception, another exception occurred:

                # Traceback (most recent call last):
                #   File "e:\Python Scripts\SaltyBot\SaltyStateMachine.py", line 35, in <module>
                #     the_json = my_thing.get_json()
                #   File "e:\Python Scripts\SaltyBot\SaltyJson.py", line 10, in get_json
                #     return self.response.json()
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\models.py", line 975, in json
                #     raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
                # requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

# TODO: EXPLOSION #2:


                # Traceback (most recent call last):
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\models.py", line 971, in json
                #     return complexjson.loads(self.text, **kwargs)
                #   File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.2800.0_x64__qbz5n2kfra8p0\lib\json\__init__.py", line 346, in loads
                #     return _default_decoder.decode(s)
                #   File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.2800.0_x64__qbz5n2kfra8p0\lib\json\decoder.py", line 337, in decode
                #     obj, end = self.raw_decode(s, idx=_w(s, 0).end())
                #   File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.2800.0_x64__qbz5n2kfra8p0\lib\json\decoder.py", line 355, in raw_decode
                #     raise JSONDecodeError("Expecting value", s, err.value) from None
                # json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

                # During handling of the above exception, another exception occurred:

                # Traceback (most recent call last):
                #   File "e:\Python Scripts\SaltyBot\SaltyStateMachine.py", line 38, in <module>
                #     the_json = my_thing.get_json()
                #   File "e:\Python Scripts\SaltyBot\SaltyJson.py", line 10, in get_json
                #     return self.response.json()
                #   File "C:\Users\Anon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\requests\models.py", line 975, in json
                #     raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
                # requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

# TODO: END OF GAME MODE STILL NOT RECORDING:
                # Currently in Tournament with 0 matches remaining.  Game state is locked.
                # Currently in Tournament with 0 matches remaining.  Game state is locked.
                # Currently in Exhibition with 25 matches remaining.  Game state is 1.
                # In Exhibitions, nothing is recorded, and no bets are placed.
                # Currently in Exhibition with 25 matches remaining.  Game state is 1.
                # In Exhibitions, nothing is recorded, and no bets are placed.
                # Currently in Exhibition with 25 matches remaining.  Game state is 1.

# NOTE: GENERAL QUESTIONS / THINGS.
# TODO: Any way to make it so that for any general explosions, to kill and restart the process?
# TODO: A way to stop the last match in a game mode earlier than have it become a super outlier for matchTime:
#       SaltyBet: Exhibitions will start shortly. Thanks for watching!
# TODO: Eventually make it so we can read twitch chat continously at the same time my program runs
# TODO: Make a requirements and a readme?
        