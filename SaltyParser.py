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
             print(f"Traditional gamestate not found.  Gamestate = {json_status}. Betting isn't open, betting isn't closed, or Player 1 or Player 2 didn't win.  Did a tie occur?")
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
        exhib_split = self.json_dict["remaining"].split(' ')[1]
        exhib_endsin = self.json_dict["remaining"].endswith('exhibition match!')
        if (exhib_endsin == True) or (exhib_split == "exhibition"):
            return True
        else:
            return False
    
    def is_tourney(self):
        reverse_split = self.json_dict["remaining"].rsplit(' ', 1)[-1]
        remaining_split = self.json_dict["remaining"].split(' ')[0]
        if (reverse_split == "bracket!") or (remaining_split == "FINAL"):
            return 1       
        else:
            return 0
        
    def get_tourney_remaining(self):
        if self.get_matches_remaining() != 1:
            self.tourney_remaining = self.get_matches_remaining() - 1
        elif self.get_matches_remaining() == 1:
            self.tourney_remaining = self.get_matches_remaining()
        else:
            self.tourney_remaining = 0
        return self.tourney_remaining 

    def get_matches_remaining(self):
        remaining_value = self.json_dict["remaining"].split(' ', 1)[0]
        if (remaining_value.isdigit()):
            return int(remaining_value)
        else:
            return 1

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
            
    def gameMode_printer(self, game_state, p1DB_ratings, p2DB_ratings, p1DB_streak, p2DB_streak, p1_probability, balance):
        table = [["Player 1:", p1DB_ratings.mu, p1DB_ratings.sigma, p1DB_streak], ["Player 2:", p2DB_ratings.mu, p2DB_ratings.sigma, p2DB_streak]]
        if (self.get_gameMode() == "Tournament"):
            print(f"Currently in {self.get_gameMode()} with {self.get_tourney_remaining()} matches remaining.  Game state is {self.get_gamestate()}.")
            if game_state == "open":
                print(tabulate(table, headers=["Fighter","Skill","Variation","Streak"], tablefmt="grid", stralign="center", numalign="decimal"))
                print(f"Player 1 chance to win: {round(100 * p1_probability, 2)}%")
                print(f"Current Balance is: {balance}")    
        elif (self.get_gameMode() == "Matchmaking"):
            print(f"Currently in {self.get_gameMode()} with {self.get_matches_remaining()} matches remaining.  Game state is {self.get_gamestate()}.")
            if game_state == "open":
                print(tabulate(table, headers=["Fighter","Skill","Variation","Streak"], tablefmt="grid", stralign="center", numalign="decimal"))
                print(f"Player 1 chance to win: {round(100 * p1_probability, 2)}%")
                print(f"Current Balance is: {balance}")