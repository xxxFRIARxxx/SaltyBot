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
                    p1tier INT,
                    p1tourney INT,
                    p2name TEXT,
                    p2odds FLOAT,
                    p2win INT,
                    p2streak INT,
                    p2mu FLOAT,
                    p2sigma FLOAT,
                    p2tier INT,
                    p2tourney INT,
                    matchLength INT,
                    betOutcome INT
                );
            """)
               
        def record_match(self, p1name, p1odds, p1winstatus, p2name, p2odds, p2winstatus, adj_p1winstreak, adj_p2winstreak, adj_p1_tier, adj_p2_tier, p1mu, p1sigma, p2mu, p2sigma, matchTime, betOutcome, is_tourney):  
            sql = 'INSERT INTO CHARDB (p1name, p1odds, p1win, p1streak, p1mu, p1sigma, p1tier, p1tourney, p2name, p2odds, p2win, p2streak, p2mu, p2sigma, p2tier, p2tourney, matchLength, betOutcome) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            data = [
            (p1name, p1odds, p1winstatus, adj_p1winstreak, p1mu, p1sigma, adj_p1_tier, is_tourney, p2name, p2odds, p2winstatus, adj_p2winstreak, p2mu, p2sigma, adj_p2_tier, is_tourney, matchTime, betOutcome,)
            ]
            
            if all(variables is not None for variables in [adj_p1winstreak, adj_p2winstreak, adj_p1_tier, adj_p2_tier]): # If both player-winstreaks and tier come back successfully, record the match.
                try:
                    with self.con:
                        self.con.executemany(sql, data)
                        self.con.commit()
                        print(str(data) + "\nThe record above has been added to the DB.")
                        self.make_backup()
                except sqlite3.IntegrityError:
                    print("This match already exists in the DB.")
                self.num_from_db()                   
            else:
                print("Either winstreaks or tier didn't retrieve.  This match wasn't recorded.")
                      
        def update_match(self):  # Updates a match in the table. 
            with self.con:
                self.con.execute("UPDATE CHARDB set p1win = 'TEST_STRING' WHERE p1win = 'locked'")
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

        def num_from_db(self):  # Selects and prints out number of records in DB.
            with self.con:
                data = self.con.execute(f"""SELECT max(id) FROM CHARDB;""")
                most_recent = data.fetchall()
            print(f"There are now {most_recent[0][0]} records in the database.")            

        def make_backup(self):
            self.match_count += 1
            if self.match_count % 10 == 0:
                with self.backup_con:
                    self.con.backup(self.backup_con)              
                print("Successful DB Backup!")
              
        def get_ratings_from_DB(self, player_search):  # Gets the Mu and Sigma from the latest match, if a match exists.  # NOTE:  Can return None. (None = Default Ratings will be assigned from Bettor.)
            if self.get_most_recent(player_search) == None:
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
                data = self.con.execute(f"""SELECT * FROM CHARDB WHERE p1name = ("{player_search}") OR p2name = ("{player_search}");""")
                all_games= data.fetchall()  # Replace the single quotes, and double quotes, with escaped quotes:  ex:  player_search.replace('"', '\"')}")
                return all_games # Returns either an empty list, or a list of tuples of all matches, with each tuple containing 1 match.
