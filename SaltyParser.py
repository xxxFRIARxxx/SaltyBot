import webbrowser
from tabulate import tabulate

class SaltyJsonParser():
    def __init__(self, json_dict):
        self.json_dict = json_dict
        self.remaining = self.json_dict["remaining"]
        self.alert = self.json_dict["alert"]
        self.start_time = 0

    def get_p1name(self):
        return self.json_dict['p1name']

    def get_p2name(self):
        return self.json_dict['p2name']

    def get_p1total(self):
        p1total = self.json_dict['p1total']
        return int(p1total.replace(',', ''))

    def get_p2total(self):
        p2total = self.json_dict['p2total']
        return int(p2total.replace(',', ''))

    def get_gamestate(self):
        json_status = self.json_dict["status"]
        if json_status not in ['open', 'locked', '1', '2']:
            print(f"Traditional gamestate not found. Gamestate = {json_status}")
        return json_status

    def set_p1winstatus(self):
        if self.get_gamestate() == "1":
            return 1
        else:
            return 0

    def set_p2winstatus(self):
        if self.get_gamestate() == "2":
            return 1
        else:
            return 0

    def is_exhib(self):
        """
        Determine if the current mode is exhibition mode based on alert or remaining messages.

        Returns:
            bool: True if the mode is exhibition, otherwise False.
        """
        return (
                self.alert == "Exhibition mode start!" or
                self.remaining.endswith("exhibition matches left!") or
                self.remaining.startswith("Matchmaking mode will be activated after the next")
        )

    def is_tourney(self):
        """
        Determine if the current game is in tournament mode.

        Returns:
            int: 1 if the game is in tournament mode, 0 otherwise.
        """
        return int(any([
            self.alert == "Tournament mode start!",
            self.remaining.endswith("in the bracket!"),
            self.remaining.startswith("FINAL ROUND!"),
            not self.remaining.endswith("next tournament!") and not self.remaining.startswith(
                "Tournament mode will be activated after the next")
        ]))

    def get_tourney_remaining(self):
        if self.get_matches_remaining() != 1:
            self.tourney_remaining = self.get_matches_remaining() - 1
        elif self.get_matches_remaining() == 1:
            self.tourney_remaining = self.get_matches_remaining()
        else:
            self.tourney_remaining = 0
        return self.tourney_remaining

    def get_matches_remaining(self):
        """
        Determine the number of matches remaining based on the 'remaining' attribute.

        Returns:
            int: The number of matches remaining or 1 for known lines.
        """
        known_lines = [
            "Tournament mode will be activated after the next",
            "Matchmaking mode will be activated after the next",
            "FINAL ROUND!",
        ]

        for known_line in known_lines:
            if self.remaining.startswith(known_line):
                return 1

        remaining_value = self.remaining.split(' ', 1)[0]

        if remaining_value.isdigit():
            return int(remaining_value)
        else:
            print(f"Couldn't retrieve number of matches from: {self.remaining}")

    def get_p1odds(self):
        if self.get_p1total() > self.get_p2total():
            return round(self.get_p1total() / self.get_p2total(), 1)
        elif self.get_p1total() < self.get_p2total():
            return float(1)

    def get_p2odds(self):
        if self.get_p1total() > self.get_p2total():
            return float(1)
        elif self.get_p1total() < self.get_p2total():
            return round(self.get_p2total() / self.get_p1total(), 1)

    def get_gamemode(self):
        if self.is_exhib() is True:
            return 'Exhibition'
        elif self.is_tourney() == 1:
            return 'Tournament'
        elif (self.is_exhib() is False) and (self.is_tourney() == 0):
            return 'Matchmaking'
        else:
            print(f"Unable to parse Game Mode. {self.json_dict}")
            return 'Unknown'

    def gamemode_printer(self, p1name, p2name, p1DB_odds, p2DB_odds, p1DB_ratings, p2DB_ratings, p1DB_streak,
                         p2DB_streak, p1_probability, balance):
        table = [[p1name, p1DB_ratings.mu, p1DB_ratings.sigma, p1DB_streak, p1DB_odds],
                 [p2name, p2DB_ratings.mu, p2DB_ratings.sigma, p2DB_streak, p2DB_odds]]
        if self.get_gamemode() == "Tournament":
            print(
                f"Currently in {self.get_gamemode()} with {self.get_tourney_remaining()} matches remaining.  Game state is {self.get_gamestate()}.")
            if self.get_gamestate() == "open":
                print(tabulate(table, headers=["Fighter", "Skill", "Variation", "Streak", "Odds Avg"],
                               colalign=("center",), tablefmt="grid", stralign="center", numalign="center"))
                print(f"Player 1 chance to win: {round(100 * p1_probability, 2)}%")
                print(f"Current Balance is: ${balance:,}")
        elif self.get_gamemode() == "Matchmaking":
            print(
                f"Currently in {self.get_gamemode()} with {self.get_matches_remaining()} matches remaining.  Game state is {self.get_gamestate()}.")
            if self.get_gamestate() == "open":
                print(tabulate(table, headers=["Fighter", "Skill", "Variation", "Streak", "Odds Avg"],
                               colalign=("center",), tablefmt="grid", stralign="center", numalign="center"))
                print(f"Player 1 chance to win: {round(100 * p1_probability, 2)}%")
                print(f"Current Balance is: ${balance:,}")
        elif self.get_gamemode() == "Exhibition":
            print(
                f"No bets are placed, and nothing is recorded in Exhibitions.  {self.get_matches_remaining()} matches remaining.  Game state is {self.get_gamestate()}")