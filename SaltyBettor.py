import math

from trueskill import Rating, rate_1vs1
from statistics import NormalDist
import decimal


class SaltyBettor():
    def __init__(self):
        self.predicted_w = None
        self.suggested_player = None
        self.suggested_wager = 1
        self.upset_bet = False
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

    def _calculate_kelly_fractions(self, p_winner, odds_winner, p_loser, odds_loser):
        k_fraction_winner = ((p_winner * odds_winner) - (1 - p_winner)) / odds_winner
        k_fraction_loser = ((p_loser * odds_loser) - (1 - p_loser)) / odds_loser
        return k_fraction_winner, k_fraction_loser

    def _calculate_suggested_wagers(self, k_fraction_winner, k_fraction_loser, balance, risk_adjust):
        k_suggest_winner = risk_adjust * (k_fraction_winner * balance)
        k_suggest_loser = risk_adjust * (k_fraction_loser * balance)
        return k_suggest_winner, k_suggest_loser

    def _quantize_value(self, value):
        return decimal.Decimal(value).quantize(decimal.Decimal("0"), rounding=decimal.ROUND_UP)

    def kelly_bet(self, p1_probability, p1_odds_avg, p2_odds_avg, balance, predicted_winner, game_mode):
        self.upset_bet = False
        if not all([p1_odds_avg, p2_odds_avg]):
            # average odds is around ~2.2 based on 400k matches
            p1_odds_avg = p2_odds_avg = 2

        if predicted_winner is None or p1_probability == 0.5:
            self.suggested_wager = 1
            return

        p_winner, p_loser, odds_winner, odds_loser = (
            (p1_probability, 1 - p1_probability, 1 / p1_odds_avg, p1_odds_avg) if p1_probability > 0.5
            else (1 - p1_probability, p1_probability, 1 / p2_odds_avg, p2_odds_avg)
        )

        risk_adjust = 0.5

        k_fraction_winner, k_fraction_loser = self._calculate_kelly_fractions(p_winner, odds_winner, p_loser,
                                                                              odds_loser)

        k_suggest_winner, k_suggest_loser = self._calculate_suggested_wagers(k_fraction_winner, k_fraction_loser,
                                                                             balance, risk_adjust)

        if (game_mode == "Tournament" and self.balance < 20000 or game_mode == "Matchmaking" and self.balance < 10000):
            self.suggested_wager = self.balance
        elif game_mode != "Tournament":
            if k_fraction_winner > 0 and k_fraction_loser > 0:
                self.suggested_wager = self._quantize_value(k_suggest_winner)
                self.upset_bet = False
            elif k_fraction_winner < 0 and k_fraction_loser > 0:
                self.suggested_wager = self._quantize_value(k_suggest_loser)
                self.upset_bet = True
            elif k_fraction_winner < 0 and k_fraction_loser < 0:
                self.upset_bet = False
                self.suggested_wager = 1

        return self.suggested_wager

    def format_bet(self, predicted_winner, suggested_bet):
        p1name = {'selectedplayer': 'player1'}
        p2name = {'selectedplayer': 'player2'}
        self.wager = {'wager': suggested_bet}
        self.suggested_player = None

        if predicted_winner is None:
            self.suggested_player = p1name  # Red wins in a draw, so this provides a minuscule advantage
        elif p1name["selectedplayer"] == predicted_winner:
            self.suggested_player = p1name if not self.upset_bet else p2name
            if self.upset_bet:
                print("Kelly bet suggests upset bet!")
        elif p2name["selectedplayer"] == predicted_winner:
            self.suggested_player = p2name if not self.upset_bet else p1name
            if self.upset_bet:
                print("Kelly bet suggests upset bet!")

        # Returns the format necessary for betting on SaltyBet.com: {:} | {:}
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
