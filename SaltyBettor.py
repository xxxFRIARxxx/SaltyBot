import random
import webbrowser
import math
from trueskill import Rating, rate_1vs1
from statistics import NormalDist

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

    def probability_of_p1_win(self, p1mu, p1sigma, p2mu, p2sigma): # Uses the cumulative distribution function of a normal distribution to determine probability of p1 winning.
        prob_P1 = None
        deltaMu = (p1mu - p2mu)                   
        sumSigma = (p1sigma**2) + (p2sigma**2)  
        playerCount = 2                                               
        denominator = math.sqrt(playerCount * (4.166666666666667 * 4.166666666666667) + sumSigma)   
        prob_P1 = NormalDist().cdf(deltaMu/denominator)
        print(f"Player 1 has a {round(100 * prob_P1, 2)}% chance of winning.")
        return prob_P1

    def predicted_winner(self, p1_probability, p1_json, p2_json, p1DB_streak, p2DB_streak): # Predicts winner first through probability of winning,  then through streaks (simple).
        self.predicted_w = None
        player1_dict = {p1_json:'player1'}
        player2_dict = {p2_json:'player2'}
        if p1_probability > .5:
            self.predicted_w = player1_dict[p1_json]
        elif p1_probability < .5:
            self.predicted_w = player2_dict[p2_json]
        elif p1_probability == .5:
            if (p1DB_streak == None) or (p2DB_streak == None): # If either of the streaks come back None once probability is already 50:50:
                self.predicted_w = None
            elif p1DB_streak > p2DB_streak:
                self.predicted_w = player1_dict[p1_json] 
            elif p2DB_streak > p1DB_streak:
                self.predicted_w = player2_dict[p2_json]
            else:
                self.predicted_w = None
        return self.predicted_w

    # Streaks first:
                
    # def suggested_bet(self, p1_probability, p1DB_streak, p2DB_streak, game_mode):
    #     suggested_wager = 1
    #     if (game_mode == 'Tournament') and (self.balance < 20000):
    #         suggested_wager = self.balance
    #     elif (p1DB_streak == None) or (p2DB_streak == None): # If either streak comes back None, use probability
    #         if p1_probability == None: 
    #             suggested_wager = 1
    #         elif p1_probability == .5:
    #             suggested_wager = 1
    #         else:
    #             suggested_wager = round((.01 * self.balance) * abs(.5 - p1_probability))

    #     elif p1DB_streak != p2DB_streak:
    #         suggested_wager = round((.01*self.balance) + ((.01*self.balance) * (.1*abs((p1DB_streak-p2DB_streak)))))
    #     elif p1_probability == None:
    #         suggested_wager = 1
    #     elif p1_probability == .5:
    #         suggested_wager = 1
    #     else:
    #         suggested_wager = round((.01 * self.balance) * abs(.5 - p1_probability))
    #     return suggested_wager            
    

    # Probabilities first:
              
    def suggested_bet(self, p1_probability, p1DB_streak, p2DB_streak, game_mode):
        suggested_wager = 1
        if (game_mode == 'Tournament') and (self.balance < 20000):
            suggested_wager = self.balance
        elif p1_probability == None:
            suggested_wager = 1
        elif p1_probability == .5:
            if (p1DB_streak is not None) and (p2DB_streak is not None): # If probability of P1 and P2 is the same, (thru default ratings, or same ratings found in DB earlier), AND if BOTH P1streak or P2streak comes back from DB
                if p1DB_streak != p2DB_streak:
                    suggested_wager = round(((.01*self.balance) * (.1*abs(p1DB_streak-p2DB_streak))))
                else:
                    suggested_wager = 1
            else:
                suggested_wager = 1
        elif p1_probability != .5:
            suggested_wager = round((.01 * self.balance) * abs(.5 - p1_probability))
        else:
            print("This prints when the suggested wager wasn't set by suggested_wager()")
        return suggested_wager

    def format_bet(self, predicted_w, suggested_wager):
        self.p1name = {'selectedplayer': 'player1'}
        self.p2name = {'selectedplayer': 'player2'}   
        self.wager = {'wager': suggested_wager}
        if predicted_w == None: # If ratings from the DB are both default thru bettor earlier or they're found and both the same, AND if NEITHER P1streak or P2 streak comes back from DB
            self.suggested_player = random.choice([self.p1name, self.p2name])
        elif self.p1name["selectedplayer"] == predicted_w:
            self.suggested_player = self.p1name
        elif self.p2name["selectedplayer"] == predicted_w:
            self.suggested_player = self.p2name
        return self.suggested_player | self.wager # Returns in the format neccessary for bet-placement on SaltyBet.com: {:} | {:}

    def set_player_rating(self, db_result):  # Sets player ratings for current match.
        if db_result == None:  
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