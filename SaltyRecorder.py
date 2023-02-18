import sqlite3
from SaltyParser import SaltyJsonParser
from SaltySocket import SaltySocket


class SaltyRecorder(): 
        def __init__(self):
            self.match_count = 0
            self.con = sqlite3.connect('SaltDatabase.db')
            self.backup_con = sqlite3.connect('SaltDatabaseBU.db')
            with self.con:
                self.con.execute("""CREATE TABLE IF NOT EXISTS CHARDB (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    p1name TEXT,
                    p1odds FLOAT,
                    p1win INT,
                    p1streak INT,
                    p1mu FLOAT,
                    p1sigma FLOAT,
                    p2name TEXT,
                    p2odds FLOAT,
                    p2win INT,
                    p2streak INT,
                    p2mu FLOAT,
                    p2sigma FLOAT,
                    matchLength INT,
                    betOutcome INT,
                    tier INT,
                    tourneyFlag INT
                );
            """)
        
        
        def record_match(self, my_parser: SaltyJsonParser, p1winstreak, p2winstreak, p1mu, p1sigma, p2mu, p2sigma, matchTime: int, betOutcome, game_tier):  
            sql = 'INSERT INTO CHARDB (p1name, p1odds, p1win, p1streak, p1mu, p1sigma, p2name, p2odds, p2win, p2streak, p2mu, p2sigma, matchLength, betOutcome, tier, tourneyFlag) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            data = [
            (my_parser.get_p1name(), my_parser.get_p1odds(), my_parser.set_p1winstatus(), self.adj_p1winstreak, p1mu, p1sigma, my_parser.get_p2name(), my_parser.get_p2odds(), my_parser.set_p2winstatus(), self.adj_p2winstreak, p2mu, p2sigma, matchTime, betOutcome, game_tier, my_parser.is_tourney())
            ]
            
            if all(variables is not None for variables in [self.adj_p1winstreak, self.adj_p2winstreak, game_tier]): # If both player-winstreaks and tier come back successfully, record the match.
                try:
                    with self.con:
                        self.con.executemany(sql, data)
                        self.con.commit()
                        print(str(data) + "\nThe record above has been added to the DB.")
                    # self.print_db()
                    self.make_backup()
                except sqlite3.IntegrityError:
                    print("This match already exists in the DB.")
            else:
                print("Either winstreaks or tier didn't retrieve.  This match wasn't recorded.")
                
        
        def update_match(self):  # Updates a match in the table. 
            with self.con:
                self.con.execute("UPDATE CHARDB set p1win = 'BONGLOAD' WHERE p1win = 'locked'")
                self.con.commit()

        def delete_match(self):  # Deletes a match from the table (leaves blank row).
            with self.con:
                self.con.execute("DELETE from CHARDB where ID <= 1000;")
                print("Total number of rows deleted:", self.con.total_changes)

        def print_db(self):  # Selects and prints out entire table
            with self.con:
                data = self.con.execute("SELECT * from CHARDB")
                for row in data:
                    print(row)

        def make_backup(self):
            self.match_count += 1
            if self.match_count % 10 == 0:
                with self.backup_con:
                    self.con.backup(self.backup_con)              
                print("Successful DB Backup!")
              
        def get_ratings_from_DB(self, player_search):  # Gets the Mu and Sigma from the latest match, if a match exists.  # NOTE:  Can return None. (None = Default Ratings will be assigned from Bettor.)
            if self.get_most_recent(player_search) == []:
                player_mu = None
                player_sigma = None
            elif self.get_most_recent(player_search)[0]['p1name'] == player_search:
                player_mu = self.get_most_recent(player_search)[0]['p1mu']
                player_sigma = self.get_most_recent(player_search)[0]['p1sigma']
            elif self.get_most_recent(player_search)[0]['p2name'] == player_search:
                player_mu = self.get_most_recent(player_search)[0]['p2mu']
                player_sigma = self.get_most_recent(player_search)[0]['p2sigma']
            return (player_mu, player_sigma) # Returns either None (if no previous match is in the DB), or the selected player's Mu and Sigma.
                
        def get_most_recent(self, player_search):  # Gets the most-recent match for a specified player from the DB, if it exists anywhere (in p1name or p2name).  (Returns empty list if no matches found.)       
            if self.get_player_matches(player_search) != []:  # If a match exists previously in the DB for the selected player.
                with self.con:
                    data = self.con.execute(f"""SELECT *, max(id) as latest FROM CHARDB WHERE p1name = ("{player_search}") OR p2name = ("{player_search}");""")
                    most_recent = data.fetchall()
                keys = ["id", "p1name", "p1odds", "p1win", "p1streak", "p1mu", "p1sigma", "p2name", "p2odds", "p2win", "p2streak", "p2mu", "p2sigma", "matchLength", "betOutcome", "tier", "tourneyFlag"]
                dict_list = []
                for i in range(len(most_recent)):
                    dict_list.append(dict(zip(keys, most_recent[i])))
                return dict_list  # Returns either an empty list, or a list of 1 dictionary containing the latest match for specified player.
            
        def get_player_matches(self, player_search):  # Gathers ALL games of a selected player from the DB .  
            with self.con:
                data = self.con.execute(f"""SELECT * FROM CHARDB WHERE p1name = ("{player_search}") OR p2name = ("{player_search}");""")  # TODO: THIS is where we introduce '' to the player names into the DB, B/C it needs them, AND the formatting of " to input to the DB.
                all_games= data.fetchall()  # Replace the single quotes, and double quotes, with escaped quotes:  ex:  player_search.replace('"', '\"')}")
                return all_games # Returns either an empty list, or a list of tuples of all matches, with each tuple containing 1 match.

        def adjust_winstreak(self, my_parser: SaltyJsonParser, my_socket: SaltySocket):  # TODO: put this in SaltySocket instead of SaltyRecorder # TODO: Return the values of adj_winstreaks  TODO: get rid of my parser and my socket parameters (too general) to winstreaks and winstatus.
            self.adj_p1winstreak = my_socket.p1winstreak
            self.adj_p2winstreak = my_socket.p2winstreak
            if (self.adj_p1winstreak == None) or (self.adj_p2winstreak == None):
                pass
            elif (self.adj_p1winstreak < 0) and (my_parser.set_p1winstatus() == 1):
                self.adj_p1winstreak = 1
            elif (self.adj_p1winstreak < 0) and (my_parser.set_p1winstatus() == 0):
                self.adj_p1winstreak = (self.adj_p1winstreak - 1)           
            elif (self.adj_p1winstreak > 0) and (my_parser.set_p1winstatus() == 1):
                self.adj_p1winstreak = (self.adj_p1winstreak + 1) 
            elif (self.adj_p1winstreak > 0) and (my_parser.set_p1winstatus() == 0):
                self.adj_p1winstreak = -1
            else:
                print("This prints if P1 winstreak hasn't been adjusted for some reason.")
        
            if (self.adj_p1winstreak == None) or (self.adj_p2winstreak == None):
                pass
            elif (self.adj_p2winstreak < 0) and (my_parser.set_p2winstatus() == 1):
                self.adj_p2winstreak = 1
            elif (self.adj_p2winstreak < 0) and (my_parser.set_p2winstatus() == 0):
                self.adj_p2winstreak = (self.adj_p2winstreak - 1)       
            elif (self.adj_p2winstreak > 0) and (my_parser.set_p2winstatus() == 1):
                self.adj_p2winstreak = (self.adj_p2winstreak + 1) 
            elif (self.adj_p2winstreak > 0) and (my_parser.set_p2winstatus() == 0):
                self.adj_p2winstreak = -1
            else:
                print("This prints if P2 winstreak hasn't been adjusted for some reason.")

# TODO APOHSTROPHIES -  KINDA FIXED, BUT NOT? :
                # (93, 'Strike freedom nitori', 1.8, 0, -4, 20.604167980000835, 7.171475587326195, 'Toki 2', 1.0, 1, 1, 29.39583201999916, 7.171475587326195, 309, 1)
                # (94, "Black_k'", 2.2, 0, -1, 20.604167980000835, 7.171475587326195, 'B.jenet motw', 1.0, 1, 1, 29.39583201999916, 7.171475587326195, 115, 1)
# TODO: Apohstrophies in player names break recorder (get_player_matches): (Kinda fixed using " instead of ' surrounding function call for pl/p2)
                #  see:  https://stackoverflow.com/questions/45575608/python-sqlite-operationalerror-near-s-syntax-error
                #  Can I just use triple quotes in    recorder.get_player_matches  -> player_formatted = f"\'{player_search}\'"   - No...no I may not, lol.
