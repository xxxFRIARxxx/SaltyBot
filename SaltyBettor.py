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

    def decide_bet(self, gameMode, p1_json, p2_json): # TODO: Rename to format_bet, and control betting decision-logic in a new f(x)
        self.p1name = {'selectedplayer': 'player1'}
        self.p2name = {'selectedplayer': 'player2'}
        self.wager = 0
        self.suggested_player = random.choice([self.p1name,self.p2name])             
        if (gameMode == 'Matchmaking'):
            self.wager = {'wager': 1}
            return self.suggested_player | self.wager
        elif (gameMode == 'Tournament'):
            self.wager = {'wager': 1}#self.balance} NOTE: CAREFUL WITH THIS VALUE UNTIL LAST-MATCH ISSUE AND SALTY-BET BUG IS FIGURED OUT - MAY BET ENTIRE NORMAL POOL ON TOURNEY.
            self.suggested_player, self.wager
            return self.suggested_player | self.wager # Returns the suggested player from the decision-logic (TBD), and suggested wager.  RETURNS IN THE FORMAT NECESSARY FOR BET PLACEMENT ON WEBSITE: {:} | {:}

    def set_player_rating(self, db_result):  # Sets player ratings for current match.  # TODO: Change name from "set" to "get".
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