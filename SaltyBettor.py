import random
from trueskill import Rating, rate_1vs1, quality_1vs1
import webbrowser

class SaltyBettor():
    def __init__(self):
        self.balance = 0
        self.outcome = 0

    def set_balance(self, balance_value):
        self.balance = balance_value
        print(f"Balance is: {self.balance}")

    def bet_outcome(self, p1_json, p2_json, game_state):
        player1_dict = {p1_json:'player1'}
        player2_dict = {p2_json:'player2'}
        if game_state == "1":
            winner = player1_dict[p1_json]
        elif game_state == "2":
            winner = player2_dict[p2_json]
        else:
            webbrowser.open("https://www.saltybet.com/state.json")
            print(game_state)
            print('This prints when no player has won the match.  (Draw?) This message comes from bettor -> bet_outcome')       
        if self.suggested_player['selectedplayer'] == winner:
            print('YOU WON THE BET')
            self.outcome = 1
        else:
            print('You lost the bet.')
            self.outcome = 0
    # TODO: Separate out wager logic into new f(x), and rename predicted_winner to predicted_winner

    def suggested_wager(self):
        if self.predicted_winner() is not None:
            pass

    def predicted_winner(self, p1rating, p2rating, p1_json, p2_json, p1DB_streak, p2DB_streak):
        player1_dict = {p1_json:'player1'}
        player2_dict = {p2_json:'player2'}
        if p1rating.mu > p2rating.mu:
            predicted_w = player1_dict[p1_json]
        elif p2rating.mu > p1rating.mu:
            predicted_w = player2_dict[p2_json]
        elif p1rating.mu == p2rating.mu:
            if (p1DB_streak is not None) or (p2DB_streak is not None): # If either P1streak or P2streak comes back from DB
                if p1DB_streak > p2DB_streak:
                    predicted_w = player1_dict[p1_json] 
                elif p2DB_streak > p1DB_streak:
                    predicted_w = player2_dict[p2_json]
                else:
                    predicted_w = None
            else: # If ratings from the DB are both default thru bettor earlier or they're found and both the same, AND if neither P1streak or P2 streak come back from DB
                predicted_w = None
        return predicted_w

    def format_bet(self, gameMode, predicted_w):
        self.p1name = {'selectedplayer': 'player1'}
        self.p2name = {'selectedplayer': 'player2'}
        self.wager_amount = 0
        if predicted_w == None: # If ratings from the DB are both default thru bettor earlier or they're found and both the same, AND if neither P1streak or P2 streak come back from DB
            self.suggested_player = random.choice([self.p1name, self.p2name])
            self.wager_amount = 10
        elif self.p1name["selectedplayer"] == predicted_w:
            self.suggested_player = self.p1name
            self.wager_amount = 100
        elif self.p2name["selectedplayer"] == predicted_w:
            self.suggested_player = self.p2name
            self.wager_amount = 100
                 
        if (gameMode == 'Matchmaking'):
            self.wager = {'wager': self.wager_amount}
            return self.suggested_player | self.wager
        elif (gameMode == 'Tournament'):
            self.wager = {'wager': (self.wager_amount * 10)}#self.balance} NOTE: CAREFUL WITH THIS VALUE UNTIL LAST-MATCH ISSUE AND SALTY-BET BUG IS FIGURED OUT - MAY BET ENTIRE NORMAL POOL ON TOURNEY.
            # self.suggested_player, self.wager # TODO: Can I delete this?  Might have put this here on accident way back when.
            return self.suggested_player | self.wager # Returns the suggested player from the decision-logic (TBD), and suggested wager.  RETURNS IN THE FORMAT NECESSARY FOR BET PLACEMENT ON WEBSITE: {:} | {:}

    def get_player_rating(self, db_result):  # Sets player ratings for current match.
        if db_result == None:  
            self.rating = Rating() # TODO:  Eventually (with enough data) update Rating() averages with true averages from DB?  (With original default values as a "floor"?.  IDK wtf I'm talking about probably.)     
        else:
            self.rating = Rating(db_result[0],db_result[1])
        return self.rating # Returns either the default rating if none is found in the DB, or the rating of the selected player from their Mu and Sigma pulled from the DB.
    
    def update_ranking_after(self, gameState, p1finalinput, p2finalinput):  # Updates rankings of both players after current match is over.
        if gameState == "1":
            p1final, p2final = rate_1vs1(p1finalinput, p2finalinput)
            print("Player 1 wins!")
        elif gameState == "2":
            p2final, p1final = rate_1vs1(p2finalinput, p1finalinput)
            print("Player 2 wins!")
        return p1final, p2final # Returns final Ratings objects of each player from the current match after completion.  Ratings objects contain updated Mu and Sigma values.  
    







#Anyway, if you need to calculate a win probability between only 2 teams, this code snippet will help you:

# import itertools
# import math

# def win_probability(team1, team2):
#     delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
#     sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
#     size = len(team1) + len(team2)
#     denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
#     ts = trueskill.global_env()
#     return ts.cdf(delta_mu / denom)


# The following seems to produce good results. (It's Jeff Moser's suggestion in the comments of http://www.moserware.com/2010/03/computing-your-skill.html, translated to Python).

# def win_probability(a, b):                                                      
#     deltaMu = sum([x.mu for x in a]) - sum([x.mu for x in b])                   
#     sumSigma = sum([x.sigma ** 2 for x in a]) + sum([x.sigma ** 2 for x in b])  
#     playerCount = len(a) + len(b)                                               
#     denominator = math.sqrt(playerCount * (BETA * BETA) + sumSigma)             
#     return cdf(deltaMu / denominator)  


# For 1v1 matchup, I believe it should look like this (untested):

# from math import sqrt
# from trueskill import Rating, TrueSkill, global_env

# def p_win_1v1(p1: Rating,p2: Rating,draw_margin: float,n: int = 2, env: Trueskill = None,) -> float:
#     """Calculate the probability that p1 wins the game."""
#     if env is None:
#         env = global_env()
#     return 1env.cdf((p1.mu - p2.mu - draw_margin) / sqrt(n * env.beta**2 + p1.sigma**2 + p2.sigma**2))