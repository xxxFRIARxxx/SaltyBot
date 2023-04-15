import webbrowser
from tabulate import tabulate

class SaltyJsonParser():
    def __init__(self, json_dict):
        self.json_dict = json_dict
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
        # "open", "locked", "1", "2"
        json_status = self.json_dict["status"]
        if json_status in ['open', 'locked', '1', '2']:
            return json_status
        else:
             webbrowser.open("https://www.saltybet.com/state.json")
             print(f"Traditional gamestate not found.  Gamestate = {json_status}. Betting isn't open, betting isn't closed, or Player 1 or Player 2 didn't win.  Did SB break?")
             print(json_status)
             return json_status

    def set_p1winstatus(self):
            if (self.get_gamestate() == "1"):
                return 1
            else:
                return 0
        
    def set_p2winstatus(self):
        if (self.get_gamestate() == "2"):
            return 1
        else:
            return 0

    def is_exhib(self):
        if self.alert == "Exhibition mode start!":
            return True
        elif self.remaining.endswith("exhibition matches left!"):
            return True
        elif self.remaining.startswith(
                "Matchmaking mode will be activated after the next"
        ):
            return True
        else:
            return False
        # try:
        #     if (self.json_dict["remaining"].split(' ')[1] == "exhibition") or (self.json_dict["remaining"].endswith('exhibition match!')):
        #         return True
        #     else:
        #         return False
        # except:
        #     print(self.json_dict)
        #     raise Exception("JSON Dict failure")
            
    def is_tourney(self):
        if not any([self.json_dict["alert"] == "Tournament mode start!", self.json_dict["remaining"].endswith("in the bracket!"), (self.json_dict["remaining"].startswith("FINAL ROUND!"))]):
            return 0
        else:
            return 1
        # if self.json_dict["alert"] == "Tournament mode start!":
        #     return 1
        # elif self.json_dict["remaining"].endswith("in the bracket!") or (self.json_dict["remaining"].startswith("FINAL ROUND!")):
        # # if (self.json_dict["remaining"].rsplit(' ', 1)[-1] == "bracket!") or (self.json_dict["remaining"].split(' ')[0] == "FINAL"):
        #     return 1
        # else:
        #     return 0
        
    def get_tourney_remaining(self):
        if self.get_matches_remaining() != 1:
            self.tourney_remaining = self.get_matches_remaining() - 1
        elif self.get_matches_remaining() == 1:
            self.tourney_remaining = self.get_matches_remaining()
        else:
            self.tourney_remaining = 0
        return self.tourney_remaining 

    def get_matches_remaining(self):
        for known_line in [
            "Tournament mode will be activated after the next",
            "Matchmaking mode will be activated after the next",
            "FINAL ROUND!",
        ]:
            if self.json_dict["remaining"].startswith(known_line):
                return 1
        remaining_value = self.json_dict["remaining"].split(' ', 1)[0]
        if (remaining_value.isdigit()):
            return int(remaining_value)
        else:
            print("Couldn't retrieve number of matches.")

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

    def get_gameMode(self):
        if self.is_exhib() is True:
            game_mode = 'Exhibition'
            return game_mode
        elif (self.is_tourney() == 1):
            game_mode = 'Tournament'
            return game_mode
        elif (self.is_exhib() is False) and (self.is_tourney() == 0):
            game_mode = 'Matchmaking' 
            return game_mode
        else:
            print("SaltyBet probably broke.  This means that it's not MM, Exhib, OR a Tourney.")
            
    def gameMode_printer(self, p1name, p2name, p1DB_odds, p2DB_odds, p1DB_ratings, p2DB_ratings, p1DB_streak, p2DB_streak, p1_probability, balance):
        table = [[p1name, p1DB_ratings.mu, p1DB_ratings.sigma, p1DB_streak, p1DB_odds], [p2name, p2DB_ratings.mu, p2DB_ratings.sigma, p2DB_streak, p2DB_odds]]
        if (self.get_gameMode() == "Tournament"):
            print(f"Currently in {self.get_gameMode()} with {self.get_tourney_remaining()} matches remaining.  Game state is {self.get_gamestate()}.")
            if self.get_gamestate() == "open":
                print(tabulate(table, headers=["Fighter","Skill","Variation","Streak","Odds Avg"], colalign=("center",), tablefmt="grid", stralign="center", numalign="center"))
                print(f"Player 1 chance to win: {round(100 * p1_probability, 2)}%")
                print(f"Current Balance is: ${balance:,}")             
        elif (self.get_gameMode() == "Matchmaking"):
            print(f"Currently in {self.get_gameMode()} with {self.get_matches_remaining()} matches remaining.  Game state is {self.get_gamestate()}.")
            if self.get_gamestate() == "open":
                print(tabulate(table, headers=["Fighter","Skill","Variation","Streak","Odds Avg"], colalign=("center",), tablefmt="grid", stralign="center", numalign="center"))
                print(f"Player 1 chance to win: {round(100 * p1_probability, 2)}%")
                print(f"Current Balance is: ${balance:,}")
        elif (self.get_gameMode() == "Exhibition"):
            print(f"No bets are placed, and nothing is recorded in Exhibitions.  {self.get_matches_remaining()} matches remaining.  Game state is {self.get_gamestate()}")
