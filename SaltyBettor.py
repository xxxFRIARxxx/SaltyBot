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

        elif self.old_balance < self.balance:
            balance_diff = self.balance - self.old_balance
            self.old_balance = self.balance
            print(f"Last bet: You won ${balance_diff:,}")
        elif self.old_balance > self.balance:
            balance_diff = self.old_balance - self.balance
            self.old_balance = self.balance
            print(f"Last bet: You lost ${balance_diff:,}")

    def bet_outcome(self, p1_json, p2_json, game_state):
        player1_dict = {p1_json: 'player1'}
        player2_dict = {p2_json: 'player2'}
        if game_state == "1":
            winner = player1_dict[p1_json]
        elif game_state == "2":
            winner = player2_dict[p2_json]
        else:
            print(f'Possible Draw or Invalid Game State. Current Game State is {game_state}')
        if self.suggested_player['selectedplayer'] == winner:
            print('YOU WON THE BET!')
            self.outcome = 1
        else:
            print('You lost the bet.')
            self.outcome = 0

    def probability_of_p1_win(self, p1mu, p1sigma, p2mu, p2sigma):
        prob_P1 = None
        deltaMu = (p1mu - p2mu)
        sumSigma = (p1sigma ** 2) + (p2sigma ** 2)
        playerCount = 2
        beta = 4.166666666666667  # Sigma / 2
        denominator = math.sqrt(playerCount * (beta * beta) + sumSigma)
        prob_P1 = NormalDist().cdf(deltaMu / denominator)
        return prob_P1

    def prediction(self, p1mu, p2mu, p1_probability, p1_json, p2_json):
        self.predicted_w = None
        player1_dict = {p1_json: 'player1'}
        player2_dict = {p2_json: 'player2'}

        if p1mu == 25 or p2mu == 25:  # If p1 or p2 has no recorded matches
            self.predicted_w = None
        elif p1_probability > .5:
            self.predicted_w = player1_dict[p1_json]
        elif p1_probability < .5:
            self.predicted_w = player2_dict[p2_json]
        elif p1_probability == .5:
            self.predicted_w = None
        return self.predicted_w

    def kelly_bet(self, p1_probability, p1_odds_avg, p2_odds_avg, balance, predicted_winner, game_mode):
        self.suggested_wager = 1

        if balance is not None:
            if not all([p1_odds_avg, p2_odds_avg]):
                p1_odds_avg = 1
                p2_odds_avg = 1
            if p1_probability > 0.5:
                b = 1 / p1_odds_avg
                q = 1 - p1_probability
                p = p1_probability
            elif p1_probability < 0.5:
                b = 1 / p2_odds_avg
                q = p1_probability
                p = abs(p1_probability - 1)
            else:
                b = 1
                q = 0.5
                p = 0.5

            risk_adjust = 0.5
            k_fraction = ((p * b) - q) / b

            k_suggest = risk_adjust * (k_fraction*balance)
            if (game_mode == "Tournament") and (self.balance < 20000):
                self.suggested_wager = self.balance
            elif (game_mode == "Matchmaking") and (self.balance < 10000):
                self.suggested_wager = self.balance
            elif predicted_winner is None:
                self.suggested_wager = 1
            elif (predicted_winner != None) and (game_mode != "Tournament"):
                if p1_probability != .5 and k_fraction > 0:
                    self.suggested_wager = decimal.Decimal(k_suggest).quantize(decimal.Decimal('0'), rounding=decimal.ROUND_UP)
                elif (p1_probability == .5):
                    self.suggested_wager = 1
        return self.suggested_wager

    def format_bet(self, predicted_winner, suggested_bet):
        self.p1name = {'selectedplayer': 'player1'}
        self.p2name = {'selectedplayer': 'player2'}
        self.wager = {'wager': suggested_bet}
        if predicted_winner is None:
            self.suggested_player = self.p1name  # Red wins in a draw, so this provides a miniscule advantage
        if self.p1name["selectedplayer"] == predicted_winner:
            self.suggested_player = self.p1name
        elif self.p2name["selectedplayer"] == predicted_winner:
            self.suggested_player = self.p2name
        # Returns the format neccessary for betting on SaltyBet.com: {:} | {:}
        return self.suggested_player | self.wager

    def set_player_rating(self, db_result):
        if db_result is None:
            self.rating = Rating()
        else:
            self.rating = Rating(db_result[0], db_result[1])
        return self.rating

    def update_ranking_after(self, game_state, p1finalinput, p2finalinput):
        if game_state == "1":
            p1final, p2final = rate_1vs1(p1finalinput, p2finalinput)
            print("Player 1 wins!")
        elif game_state == "2":
            p2final, p1final = rate_1vs1(p2finalinput, p1finalinput)
            print("Player 2 wins!")
        return p1final, p2final
