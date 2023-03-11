import os
from SaltyJson import SaltyJson
from SaltyParser import SaltyJsonParser
from SaltyDatabase import SaltyDatabase
from SaltySocket import SaltySocket
from SaltyTimer import SaltyTimer
from SaltyWebInteractor import SaltyWebInteractor
from SaltyBettor import SaltyBettor
from SaltyReceiver import CustomThread
from SaltyPanda import SaltyPanda

my_json = SaltyJson()
database = SaltyDatabase()
my_socket = SaltySocket()
game_time = SaltyTimer()
bettor = SaltyBettor()
interactor = SaltyWebInteractor()
thread = CustomThread()
panda = SaltyPanda()

new_match = 0
match_start_time = 0
total_match_time_sec = 0

first_run = True
exiting_tourney = True
previous_game_mode = None
game_state_lies = False
previous_game_state = None
p1DB_streak = None
p2DB_streak = None


thread.start() 

while True:
    the_json = my_json.get_json()
    my_parser = SaltyJsonParser(the_json)
    game_mode = my_parser.get_gameMode()
    game_state = my_parser.get_gamestate()

    # TODO:  Are the below 2 blocks doing what they're supposed to?  Last tourney isn't recording still.
    if (game_mode != previous_game_mode):
        game_state_lies = True
    previous_game_mode = game_mode
    
    if (game_state != previous_game_state):
        game_state_lies = False
    previous_game_state = game_state
    
    if ((game_mode != 'Exhibition') and (game_state_lies is False)):
        exiting_tourney = True
        if (game_state == 'open'):
            if (new_match == 0):
                os.system('cls')
                bettor.set_balance(interactor.get_balance())
                bettor.bet_outcome_amount(first_run)
                
                first_run = False
                p1DB_ratings = bettor.set_player_rating(database.get_ratings_from_DB(my_parser.get_p1name())) # Gets Mu and Sigma for Player 1 in DB, sets them to default if there are no prior matches in the DB, and sets them accordingly if there are.
                p2DB_ratings = bettor.set_player_rating(database.get_ratings_from_DB(my_parser.get_p2name())) # Gets Mu and Sigma for Player 2 in DB, sets them to default if there are no prior matches in the DB, and sets them accordingly if there are.
                p1DB_streak = database.get_winstreaks_from_DB(my_parser.get_p1name())
                p2DB_streak = database.get_winstreaks_from_DB(my_parser.get_p2name())
                p1_probability = bettor.probability_of_p1_win(p1DB_ratings.mu, p1DB_ratings.sigma, p2DB_ratings.mu, p2DB_ratings.sigma)
                predicted_winner = bettor.predicted_winner(p1DB_ratings.mu, p2DB_ratings.mu, p1DB_ratings.sigma, p2DB_ratings.sigma, p1_probability, my_parser.get_p1name(), my_parser.get_p2name(), p1DB_streak, p2DB_streak)
                kelly_bet = bettor.kelly_bet(p1_probability, bettor.balance, predicted_winner, game_mode)
                my_parser.gameMode_printer(p1DB_ratings, p2DB_ratings, p1DB_streak, p2DB_streak, p1_probability, bettor.balance)
                interactor.place_bet_on_website(bettor.format_bet(predicted_winner, kelly_bet))
                new_match = 1
                my_socket.find_winstreak = True            
        elif (game_state == 'locked'):
            if (first_run is False):
                if (new_match == 1):
                    new_match = 2
                    game_time.timer_start()
                    my_parser.gameMode_printer(p1DB_ratings, p2DB_ratings, p1DB_streak, p2DB_streak, p1_probability, bettor.balance)
        elif (game_state == '1') or (game_state == '2'): 
            if (first_run is False):
                if (new_match == 2):
                    new_match = 0
                    game_time.timer_snapshot()
                    my_parser.gameMode_printer(p1DB_ratings, p2DB_ratings, p1DB_streak, p2DB_streak, p1_probability, bettor.balance)
                    ratings_to_db = bettor.update_ranking_after(game_state, p1DB_ratings, p2DB_ratings) # Updates ratings after the match.
                    my_socket.adjust_winstreak(my_parser.set_p1winstatus(), my_parser.set_p2winstatus(), thread.value1, thread.value2)
                    my_socket.adjust_tier(thread.value3)
                    bettor.bet_outcome(my_parser.get_p1name(), my_parser.get_p2name(), game_state)
                    database.record_match(my_parser.get_p1name(),my_parser.get_p1odds(), my_parser.set_p1winstatus(), my_parser.get_p2name(), my_parser.get_p2odds(), my_parser.set_p2winstatus(), my_socket.adj_p1winstreak, my_socket.adj_p2winstreak, my_socket.adj_p1_tier, my_socket.adj_p2_tier, ratings_to_db[0].mu, ratings_to_db[0].sigma, ratings_to_db[1].mu, ratings_to_db[1].sigma, game_time.snapshot, bettor.outcome, my_parser.is_tourney())                    
                    panda.panda_to_csv(database.db_for_pandas())
    elif ((game_mode == "Exhibition") and (game_state_lies is False)):
        if (game_state == "open"):
            if (new_match == 0):
                os.system('cls')
                print(f"In Exhibition.  No bets are placed, and nothing is recorded.  {my_parser.get_matches_remaining()} matches left.")
                new_match = 1
        elif (game_state == "locked"):
            if (new_match == 1):
                print(f"In Exhibition.  No bets are placed, and nothing is recorded.  {my_parser.get_matches_remaining()} matches left.")
                new_match = 2
        elif (game_state == "1") or (game_state == "2"):
            if (new_match == 2):
                if exiting_tourney == True:
                    database.record_match(my_parser.get_p1name(),my_parser.get_p1odds(), my_parser.set_p1winstatus(), my_parser.get_p2name(), my_parser.get_p2odds(), my_parser.set_p2winstatus(), my_socket.adj_p1winstreak, my_socket.adj_p2winstreak, my_socket.adj_p1_tier, my_socket.adj_p2_tier, ratings_to_db[0].mu, ratings_to_db[0].sigma, ratings_to_db[1].mu, ratings_to_db[1].sigma, game_time.snapshot, bettor.outcome, 1)
                    exiting_tourney = False
                print(f"In Exhibition.  No bets are placed, and nothing is recorded.  {my_parser.get_matches_remaining()} matches left.")
                new_match = 0
       
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
        