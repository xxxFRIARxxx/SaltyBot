import webbrowser
import math
from trueskill import Rating, rate_1vs1
from statistics import NormalDist
import decimal

class SaltyBettor():
    def __init__(self):
        self.balance = 0
        self.outcome = 0
        self.old_balance = 0

    def set_balance(self, balance_value):
        self.balance = balance_value

    def bet_outcome_amount(self):
        if self.old_balance == 0:
            self.old_balance = self.balance
        elif (self.old_balance < self.balance):
            balance_diff = self.balance - self.old_balance
            self.old_balance = self.balance
            print(f"Last bet: You won ${balance_diff:,}")
        elif (self.old_balance > self.balance):
            balance_diff = self.old_balance - self.balance
            self.old_balance = self.balance
            print(f"Last bet: You lost ${balance_diff:,}")

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
            print('YOU WON THE BET!')
            self.outcome = 1
        else:
            print('You lost the bet.')
            self.outcome = 0

    def probability_of_p1_win(self, p1mu, p1sigma, p2mu, p2sigma): # Uses the cumulative distribution function of a normal distribution to determine probability of p1 winning.
        prob_P1 = None
        deltaMu = (p1mu - p2mu)                   
        sumSigma = (p1sigma**2) + (p2sigma**2)  
        playerCount = 2
        beta = 4.166666666666667                                        
        denominator = math.sqrt(playerCount * (beta * beta) + sumSigma)   
        prob_P1 = NormalDist().cdf(deltaMu/denominator)
        return prob_P1

    def predicted_winner(self, p1sigma, p2sigma, p1_probability, p1_json, p2_json, p1DB_streak, p2DB_streak): # Predicts winner through probability of winning, then through difference in Sigma values, then through streaks.
        self.predicted_w = None
        player1_dict = {p1_json:'player1'}
        player2_dict = {p2_json:'player2'} 
        if p1_probability > .5:
            self.predicted_w = player1_dict[p1_json]
        elif p1_probability < .5:
            self.predicted_w = player2_dict[p2_json]
        elif p1_probability == .5:
            if p1sigma < p2sigma:
                self.predicted_w = player1_dict[p1_json]
            elif p2sigma < p1sigma:
                self.predicted_w = player2_dict[p2_json]
            elif p1sigma == p2sigma:
                if (p1DB_streak is None) or (p2DB_streak is None): # If either of the streaks come back None once probability is already 50:50 and Sigmas are the same:
                    self.predicted_w = None
                elif p1DB_streak > p2DB_streak:
                    self.predicted_w = player1_dict[p1_json]
                elif p2DB_streak > p1DB_streak:
                    self.predicted_w = player2_dict[p2_json]
                else:
                    self.predicted_w = None  
            else:
                self.predicted_w = None
        else:
            self.predicted_w = None
        return self.predicted_w

    def kelly_bet(self, p1_probability, balance, predicted_winner, game_mode):
        q = 1-p1_probability
        # b = p1_probability/(1-p1_probability)
        b = 1
        fraction = p1_probability-(q/b)
        k_suggest = abs(.05*(fraction*balance))
        if (game_mode == "Tournament") and (self.balance < 20000):
            suggested_wager = self.balance
        elif (game_mode == "Matchmaking") and (self.balance < 10000):
            suggested_wager = self.balance
        if predicted_winner is None:
            suggested_wager = 1
        elif predicted_winner != None:
            if p1_probability != .5:
                suggested_wager = decimal.Decimal(k_suggest).quantize(decimal.Decimal('0'), rounding=decimal.ROUND_UP)          
            elif (p1_probability == .5):
                suggested_wager = 1              
        return suggested_wager

    def format_bet(self, predicted_winner, suggested_bet):
        self.p1name = {'selectedplayer': 'player1'}
        self.p2name = {'selectedplayer': 'player2'}   
        self.wager = {'wager': suggested_bet}
        if predicted_winner is None: # If ratings from the DB are both default thru bettor earlier or they're found and both the same, AND their Sigmas are the same (or don't come back), AND if EITHER P1streak or P2 streak DOESN'T come back from DB OR are the same.
            self.suggested_player = self.p1name # Red wins in a draw, so this provides a miniscule advantage over random choice of a suggested winner.
        if suggested_bet > 500000:
            self.wager["wager"] = 500000
        if self.p1name["selectedplayer"] == predicted_winner:
            self.suggested_player = self.p1name
        elif self.p2name["selectedplayer"] == predicted_winner:
            self.suggested_player = self.p2name
        return self.suggested_player | self.wager # Returns in the format neccessary for bet-placement on SaltyBet.com: {:} | {:}

    def set_player_rating(self, db_result):  # Sets player ratings for current match.
        if db_result is None:  
            self.rating = Rating()
        else:
            self.rating = Rating(db_result[0],db_result[1])
        return self.rating # Returns either the default rating if none is found in the DB, or the rating of the selected player from their Mu and Sigma pulled from the DB.
    
    def update_ranking_after(self, game_state, p1finalinput, p2finalinput):  # Updates rankings of both players after current match is over.
        if game_state == "1":
            p1final, p2final = rate_1vs1(p1finalinput, p2finalinput)
            print("Player 1 wins!")
        elif game_state == "2":
            p2final, p1final = rate_1vs1(p2finalinput, p1finalinput)
            print("Player 2 wins!")
        return p1final, p2final # Returns final Ratings objects of each player from the current match after completion.  Ratings objects contain updated Mu and Sigma values.  