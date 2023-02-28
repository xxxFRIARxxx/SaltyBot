import requests
from SaltyJson import SaltyJson
from SaltyParser import SaltyJsonParser
from SaltyDatabase import SaltyRecorder
from SaltySocket import SaltySocket
from SaltyTimer import SaltyTimer
from SaltyWebInteractant import SaltyWebInteractant
from SaltyBettor import SaltyBettor
from SaltyReceiver import CustomThread

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
game_time = SaltyTimer()
bettor = SaltyBettor()
interactor = SaltyWebInteractant()
thread = CustomThread()

first_run = True
previous_game_mode = None
game_state_lies = False
previous_game_state = None
p1DB_streak = None
p2DB_streak = None

thread.start() 

while True:
    the_json = my_thing.get_json()
    my_parser = SaltyJsonParser(the_json)
    # balance = interactor.get_balance()
    game_mode = my_parser.get_gameMode()
    game_state = my_parser.get_gamestate()

    # TODO:  Are the below 2 blocks doing what they're supposed to?  Last tourney isn't recording still.
    if (game_mode != previous_game_mode):
        game_state_lies = True
    previous_game_mode = game_mode
    
    if (game_state != previous_game_state):
        game_state_lies = False
    previous_game_state = game_state
    
    if ((game_mode != 'Exhibition') and (game_state_lies == False)):
        if (game_state == 'open'):
            if (new_match == 0):
                first_run = False
                p1DB_ratings = bettor.set_player_rating(recorder.get_ratings_from_DB(my_parser.get_p1name())) # Gets Mu and Sigma for Player 1 in DB, sets them to default if there are no prior matches in the DB, and sets them accordingly if there are.
                p2DB_ratings = bettor.set_player_rating(recorder.get_ratings_from_DB(my_parser.get_p2name())) # Gets Mu and Sigma for Player 2 in DB, sets them to default if there are no prior matches in the DB, and sets them accordingly if there are.
                p1DB_streak = recorder.get_winstreaks_from_DB(my_parser.get_p1name())
                p2DB_streak = recorder.get_winstreaks_from_DB(my_parser.get_p2name())
                p1_probability = bettor.probability_of_p1_win(p1DB_ratings.mu, p1DB_ratings.sigma, p2DB_ratings.mu, p2DB_ratings.sigma)
                new_match = 1
                my_socket.find_winstreak = True
                # TODO: The line below makes this program go into hyperdrive - Is this bad?
                bettor.set_balance(interactor.get_balance()) 
                my_parser.gameMode_printer()
                # bettor.set_balance(balance) # Sets and displays current balance of your account.
                print(f"Player 1:   Mu = {p1DB_ratings.mu}  Sigma = {p1DB_ratings.sigma}  Winstreak from DB = {p1DB_streak}")
                print(f"Player 2:   Mu = {p2DB_ratings.mu}  Sigma = {p2DB_ratings.sigma}  Winstreak from DB = {p2DB_streak}")
                # TODO:  Include data regression to help compose bet here.
                interactor.place_bet_on_website(bettor.format_bet(bettor.predicted_winner(p1_probability, my_parser.get_p1name(), my_parser.get_p2name(), p1DB_streak, p2DB_streak), bettor.suggested_bet(p1_probability, p1DB_streak, p2DB_streak, game_mode))) # Decide bet, and place bet 
        elif (game_state == 'locked'):
            if (first_run == False):
                if (new_match == 1):
                    new_match = 2
                    game_time.timer_start()
                    my_parser.gameMode_printer()  
        elif (game_state == '1') or ((game_state == '2')): 
            if (first_run == False):
                if (new_match == 2):
                    my_parser.gameMode_printer()
                    new_match = 0
                    game_time.timer_snapshot()
                    ratings_to_db = bettor.update_ranking_after(game_state, p1DB_ratings, p2DB_ratings) # Updates ratings after the match.
                    my_socket.adjust_winstreak(my_parser.set_p1winstatus(), my_parser.set_p2winstatus(), thread.value1, thread.value2)
                    my_socket.adjust_tier(thread.value3)
                    bettor.bet_outcome(my_parser.get_p1name(), my_parser.get_p2name(), game_state)
                    recorder.record_match(my_parser.get_p1name(),my_parser.get_p1odds(), my_parser.set_p1winstatus(), my_parser.get_p2name(), my_parser.get_p2odds(), my_parser.set_p2winstatus(), my_socket.adj_p1winstreak, my_socket.adj_p2winstreak, my_socket.adj_p1_tier, my_socket.adj_p2_tier, ratings_to_db[0].mu, ratings_to_db[0].sigma, ratings_to_db[1].mu, ratings_to_db[1].sigma, game_time.snapshot, bettor.outcome, my_parser.is_tourney())

    elif game_mode == "Exhibition":
        my_parser.gameMode_printer()
    #     if (first_run == False):
    #         if (new_match == 2):
                # if (my_parser.get_matches_remaining() == 25) and (game_state in [1,2]):
                #     new_match = 0
                #     game_time.timer_snapshot() # TODO: Instead of calling snapshot here, get flag from SaltyBet in Twitch chat.
                #     ratings_to_db = bettor.update_ranking_after(game_state, p1DB_ratings, p2DB_ratings) # Updates ratings after the match.
                #     my_socket.adjust_winstreak(my_parser.set_p1winstatus(), my_parser.set_p2winstatus(), thread.value1, thread.value2)
                #     my_socket.adjust_tier(thread.value3)
                #     bettor.bet_outcome(my_parser.get_p1name(), my_parser.get_p2name(), game_state)
                #     recorder.record_match(my_parser.get_p1name(),my_parser.get_p1odds(), my_parser.set_p1winstatus(), my_parser.get_p2name(), my_parser.get_p2odds(), my_parser.set_p2winstatus(), my_socket.adj_p1winstreak, my_socket.adj_p2winstreak, my_socket.adj_p1_tier, my_socket.adj_p2_tier, ratings_to_db[0].mu, ratings_to_db[0].sigma, ratings_to_db[1].mu, ratings_to_db[1].sigma, game_time.snapshot, bettor.outcome, my_parser.is_tourney())


# TODO: EXPLOSION:
                # Traceback (most recent call last):
                #   File "e:\Python Scripts\SaltyBot\SaltyStateMachine.py", line 41, in <module>
                #     game_mode = my_parser.get_gameMode()
                #   File "e:\Python Scripts\SaltyBot\SaltyParser.py", line 91, in get_gameMode
                #     if self.is_exhib() is True:
                #   File "e:\Python Scripts\SaltyBot\SaltyParser.py", line 46, in is_exhib
                #     exhib_split = self.json_dict["remaining"].split(' ')[1]
                # TypeError: 'NoneType' object is not subscriptable


# TODO: Last match of tourney still doesn't record:
                # Currently in Tournament with 1 matches remaining.  Game state is locked.
                # Currently in Tournament with 1 matches remaining.  Game state is locked.
                # Currently in Tournament with 1 matches remaining.  Game state is locked.
                # Currently in Tournament with 1 matches remaining.  Game state is locked.
                # Currently in Tournament with 1 matches remaining.  Game state is locked.
                # Currently in Exhibition with 25 matches remaining.  No bets are placed and nothing is recorded.  Game state is 2.  
                # Currently in Exhibition with 25 matches remaining.  No bets are placed and nothing is recorded.  Game state is 2.  
                # Currently in Exhibition with 25 matches remaining.  No bets are placed and nothing is recorded.  Game state is 2.  
                # Currently in Exhibition with 25 matches remaining.  No bets are placed and nothing is recorded.  Game state is 2.  
                # Currently in Exhibition with 25 matches remaining.  No bets are placed and nothing is recorded.  Game state is 2.  

# NOTE: GENERAL QUESTIONS / THINGS.
# TODO: A way to stop the last match in a game mode earlier than have it become a super outlier for match_time:
#       SaltyBet: Exhibitions will start shortly. Thanks for watching!
        