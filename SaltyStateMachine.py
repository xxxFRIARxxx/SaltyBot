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
gameTime = SaltyTimer()
bettor = SaltyBettor()
interactor = SaltyWebInteractant()
thread = CustomThread()

first_run = True
previousGameMode = None
gameStateLies = False
previousGameState = None
p1DB_streak = None
p2DB_streak = None # TODO: Maybe take these out of global scope?

thread.start() 

while True:
    the_json = my_thing.get_json()
    my_parser = SaltyJsonParser(the_json)
    balance = interactor.get_balance()
    
    gameMode = my_parser.get_gameMode()  # TODO:  Is this wrong?  The below 2 blocks.
    if (gameMode != previousGameMode):
        gameStateLies = True
    previousGameMode = gameMode
    
    gameState = my_parser.get_gamestate()
    if (gameState != previousGameState):
        gameStateLies = False
    previousGameState = gameState
    
    if ((gameMode != 'Exhibition') and (gameStateLies == False)):
        if (gameState == 'open'):
            if (new_match == 0):
                first_run = False
                p1DB_ratings = bettor.set_player_rating(recorder.get_ratings_from_DB(my_parser.get_p1name())) # Gets Mu and Sigma for Player 1 in DB, sets them to default if there are no prior matches in the DB, and sets them accordingly if there are.
                p2DB_ratings = bettor.set_player_rating(recorder.get_ratings_from_DB(my_parser.get_p2name())) # Gets Mu and Sigma for Player 2 in DB, sets them to default if there are no prior matches in the DB, and sets them accordingly if there are.
                p1DB_streak = recorder.get_winstreaks_from_DB(my_parser.get_p1name())
                p2DB_streak = recorder.get_winstreaks_from_DB(my_parser.get_p2name())
                p1_probability = bettor.probability_of_p1_win(p1DB_ratings.mu, p1DB_ratings.sigma, p2DB_ratings.mu, p2DB_ratings.sigma)
                new_match = 1
                my_socket.find_winstreak = True
                bettor.set_balance(balance) # Sets and displays current balance of your account.
                print(f"Player 1 Rating:   Mu = {p1DB_ratings.mu}  Sigma = {p1DB_ratings.sigma}")
                print(f"Player 2 Rating:   Mu = {p2DB_ratings.mu}  Sigma = {p2DB_ratings.sigma}")
                # TODO:  Include data regression to help compose bet here.
                interactor.place_bet_on_website(bettor.format_bet(bettor.predicted_winner(p1_probability, my_parser.get_p1name(), my_parser.get_p2name(), p1DB_streak, p2DB_streak), bettor.suggested_bet(p1_probability, p1DB_streak, p2DB_streak, gameMode))) # Decide bet, and place bet 
        elif (gameState == 'locked'):
            if (first_run == False):
                if (new_match == 1):
                    new_match = 2
                    gameTime.timer_start()
        elif (gameState == '1') or ((gameState == '2')): 
            if (first_run == False):
                if (new_match == 2):
                    new_match = 0
                    gameTime.timer_snapshot()
                    ratings_to_db = bettor.update_ranking_after(gameState, p1DB_ratings, p2DB_ratings) # Updates ratings after the match.
                    my_socket.adjust_winstreak(my_parser.set_p1winstatus(), my_parser.set_p2winstatus(), thread.value1, thread.value2)
                    my_socket.adjust_tier(thread.value3)
                    bettor.bet_outcome(my_parser.get_p1name(), my_parser.get_p2name(), gameState)
                    recorder.record_match(my_parser.get_p1name(),my_parser.get_p1odds(), my_parser.set_p1winstatus(), my_parser.get_p2name(), my_parser.get_p2odds(), my_parser.set_p2winstatus(), my_socket.adj_p1winstreak, my_socket.adj_p2winstreak, my_socket.adj_p1_tier, my_socket.adj_p2_tier, ratings_to_db[0].mu, ratings_to_db[0].sigma, ratings_to_db[1].mu, ratings_to_db[1].sigma, gameTime.snapshot, bettor.outcome, my_parser.is_tourney())
    elif gameMode == "Exhibition":
        if (my_parser.get_matchesremaining() == 25) and (gameState in [1,2]):
            new_match = 0
            ratings_to_db = bettor.update_ranking_after(gameState, p1DB_ratings, p2DB_ratings) # Updates ratings after the match.
            my_socket.adjust_winstreak(my_parser.set_p1winstatus(), my_parser.set_p2winstatus(), thread.value1, thread.value2)
            my_socket.adjust_tier(thread.value3)
            bettor.bet_outcome(my_parser.get_p1name(), my_parser.get_p2name(), gameState)
            recorder.record_match(my_parser.get_p1name(),my_parser.get_p1odds(), my_parser.set_p1winstatus(), my_parser.get_p2name(), my_parser.get_p2odds(), my_parser.set_p2winstatus(), my_socket.adj_p1winstreak, my_socket.adj_p2winstreak, my_socket.adj_p1_tier, my_socket.adj_p2_tier, ratings_to_db[0].mu, ratings_to_db[0].sigma, ratings_to_db[1].mu, ratings_to_db[1].sigma, gameTime.snapshot, bettor.outcome, my_parser.is_tourney())

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
# TODO: Make a winstreak-difference function?  (From where their winstreak was before the match, to where it is after the match: the difference)
# TODO: A way to stop the last match in a game mode earlier than have it become a super outlier for matchTime:
#       SaltyBet: Exhibitions will start shortly. Thanks for watching!
# TODO: Make a requirements and a readme?
        