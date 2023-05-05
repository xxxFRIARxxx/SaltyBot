import webbrowser
import math
import decimal
from trueskill import Rating, rate_1vs1
from statistics import NormalDist

class SaltyBettor():
    def __init__(self):
        self.balance = 0
        self.outcome = 0
        self.old_balance = 0

    def set_balance(self, balance_value):
        self.balance = balance_value

    def bet_outcome_amount(self, gs_lies):
        if self.old_balance == 0:
            self.old_balance = self.balance
        if gs_lies == True:
            pass
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
            print(f"Gamestate is: {game_state}. This prints when no player has won the match, and should only print during a SB catastrophe. This message comes from bettor -> bet_outcome")       
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
        beta = 4.166666666666667           # Sigma / 2                             
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
    
    def prediciton(self, p1sigma, p2sigma, p1mu, p2mu, p1_probability, p1_json, p2_json, p1DB_streak, p2DB_streak, p1_odds_avg, p2_odds_avg): # Mu != 25, Mu +/- sigma, odds avg, sigma diff, streak diff
        self.predicted_w = None
        player1_dict = {p1_json:'player1'}
        player2_dict = {p2_json:'player2'} 
        if p1mu == 25 or p2mu == 25:
            self.predicted_w == None
        if not all([p1_odds_avg, p2_odds_avg, p1DB_streak, p2DB_streak]): # If any odds or streak is None or False
            self.predicted_w = None
        elif p1_probability > .5:
            self.predicted_w = player1_dict[p1_json]  
            # if (p1mu - p1sigma) > (p2mu + p2sigma): 
            #     self.predicted_w = player1_dict[p1_json]
            # elif (p1_odds_avg > (p2_odds_avg * 2)):
            #     self.predicted_w = player1_dict[p1_json]
            # elif p1sigma < p2sigma:
            #     self.predicted_w = player1_dict[p1_json]
            # elif p1DB_streak > p2DB_streak:
            #     self.predicted_w = player1_dict[p1_json]
            # else:
            #     self.predicted_w = None
        elif p1_probability < .5:
            self.predicted_w = player2_dict[p2_json]
            # if (p2mu - p2sigma) > (p1mu + p1sigma): 
            #     self.predicted_w = player2_dict[p2_json]
            # elif (p2_odds_avg > (p1_odds_avg * 2)):
            #     self.predicted_w = player2_dict[p2_json]
            # elif p2sigma < p1sigma:
            #     self.predicted_w = player2_dict[p2_json]
            # elif p2DB_streak > p1DB_streak:
            #     self.predicted_w = player2_dict[p2_json]
            # else:
            #     self.predicted_w = None
        elif p1_probability == .5 :
            if p1_odds_avg > p2_odds_avg:
                self.predicted_w = player1_dict[p1_json]
            elif p2_odds_avg > p1_odds_avg:
                self.predicted_w = player2_dict[p2_json]
            elif p1_odds_avg == p2_odds_avg: # If the odds-averages are the same
                if p1sigma < p2sigma:
                    self.predicted_w = player1_dict[p1_json]
                elif p2sigma < p1sigma:
                    self.predicted_w = player2_dict[p2_json]
                elif p1sigma == p2sigma: # If the sigmas are the same
                    if p1DB_streak > p2DB_streak:
                        self.predicted_w = player1_dict[p1_json]
                    elif p2DB_streak > p1DB_streak:
                        self.predicted_w = player2_dict[p2_json]
                    else: # If the streaks are the same
                        self.predicted_w = None  
                else:
                    self.predicted_w = None
            else:
                self.predicted_w = None
        else:
            self.predicted_w = None
        return self.predicted_w


    def kelly_bet(self, p1_probability, p1_odds_avg, p2_odds_avg, balance, predicted_winner, game_mode):
        self.upset_bet = False
        if p1_probability != 0.5:
            if p1_probability > 0.5:
                p_winner = p1_probability
                p_loser = 1 - p1_probability
                odds_winner = 1 / p1_odds_avg
                odds_loser = p1_odds_avg
            elif p1_probability < 0.5:
                p_winner = 1 - p1_probability
                p_loser = p1_probability
                odds_winner = 1 / p2_odds_avg
                odds_loser = p2_odds_avg
        else:
            self.suggested_wager = 1
            return

        b_winner = odds_winner
        q_winner = 1 - p_winner
        risk_adjust = 0.5

        k_fraction_winner = ((p_winner * b_winner) - q_winner) / b_winner
        k_suggest_winner = risk_adjust * (k_fraction_winner * balance)

        b_loser = odds_loser
        q_loser = 1 - p_loser

        k_fraction_loser = ((p_loser * b_loser) - q_loser) / b_loser
        k_suggest_loser = risk_adjust * (k_fraction_loser * balance)

        if (game_mode == "Tournament") and (self.balance < 20000):
            self.suggested_wager = self.balance
        elif (game_mode == "Matchmaking") and (self.balance < 10000):
            self.suggested_wager = self.balance
        elif predicted_winner is None or p1_probability == .5:
            self.suggested_wager = 1
        elif game_mode != "Tournament":
            if k_fraction_winner > 0 and k_fraction_loser > 0:
                self.suggested_wager = decimal.Decimal(k_suggest_winner).quantize(decimal.Decimal('0'),
                                                                                  rounding=decimal.ROUND_UP)
                self.upset_bet = False
            elif k_fraction_winner < 0 and k_fraction_loser > 0:
                self.suggested_wager = decimal.Decimal(k_suggest_loser).quantize(decimal.Decimal('0'),
                                                                                 rounding=decimal.ROUND_UP)
                self.upset_bet = True
            elif k_fraction_winner < 0 and k_fraction_loser < 0:
                self.upset_bet = False
                self.suggested_wager = 1

        return self.suggested_wager

    # def kelly_bet(self, p1_probability, p1_odds_avg, p2_odds_avg, balance, predicted_winner, game_mode):
    #     # self.suggested_wager = 1
    #     self.suggested_wager = 1

    #     if not all([p1_odds_avg, p2_odds_avg]): # TODO: if p1 odds or p2 odds don't exist in the DB (to provide avgs), set both avgs to 1.  Is this cool?
    #         p1_odds_avg = 1
    #         p2_odds_avg = 1
    #     if p1_probability > 0.5:
    #         b = 1 / p1_odds_avg # TODO: Why are we using odds average from DB? B is the proportion of the bet gained with a win. $10 on 2-1 oddds, b = $20/$10 = 2.0
    #         q = 1 - p1_probability
    #         p = p1_probability
    #     elif p1_probability < 0.5:
    #         b = 1 / p2_odds_avg
    #         q = p1_probability
    #         p = abs(p1_probability - 1) # TODO:  Isn't this the same as 1 - p1_probability?
    #     else:
    #         b = 1
    #         q = 0.5
    #         p = 0.5

    #     k_fraction = ((p * b) - q) / b # TODO: ((probability of winning * proportion of bet gained w/ a win) - probability of losing) / proportion of bet gained w/ a win
    #     k_suggest = k_fraction*balance
    #     if (game_mode == "Tournament") and (self.balance < 20000):
    #         self.suggested_wager = self.balance
    #     # elif (game_mode == "Matchmaking") and (self.balance < 10000):
    #     #     self.suggested_wager = self.balance
    #     elif predicted_winner is None:
    #         self.suggested_wager = 1
    #     elif (predicted_winner != None) and (game_mode != "Tournament"):
    #         if p1_probability != .5 and k_fraction > 0:
    #             self.suggested_wager = decimal.Decimal(k_suggest).quantize(decimal.Decimal('0'), rounding=decimal.ROUND_UP)          
    #         elif (p1_probability == .5):
    #             self.suggested_wager = 1              

    #     return self.suggested_wager

    def format_bet(self, predicted_winner, suggested_bet):
        self.p1name = {'selectedplayer': 'player1'}
        self.p2name = {'selectedplayer': 'player2'}   
        self.wager = {'wager': suggested_bet}
        if predicted_winner is None: # If ratings from the DB are both default thru bettor earlier or they're found and both the same, AND their Sigmas are the same (or don't come back), AND if EITHER P1streak or P2 streak DOESN'T come back from DB OR are the same.
            self.suggested_player = self.p1name # Red wins in a draw, so this provides a miniscule advantage over random choice of a suggested winner.
        # if suggested_bet > 20000:
        #     self.wager["wager"] = 20000
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