import sqlite3

class SaltyDatabase(): 
        def __init__(self):
            self.match_count = 0
            self.con = sqlite3.connect('SaltDatabase.db')
            self.backup_con = sqlite3.connect('SaltDatabaseBU.db')
            with self.con:
                self.con.execute("""CREATE TABLE IF NOT EXISTS SBMATCHES (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    p1name TEXT,
                    p1odds FLOAT,
                    p1win INT,
                    p1streak INT,
                    p1mu FLOAT,
                    p1sigma FLOAT,
                    p1tier INT,
                    p1tourney INT,
                    p1time INT,
                    p2name TEXT,
                    p2odds FLOAT,
                    p2win INT,
                    p2streak INT,
                    p2mu FLOAT,
                    p2sigma FLOAT,
                    p2tier INT,
                    p2tourney INT,
                    p2time INT,
                    betOutcome INT
                );
            """)
               
        def record_match(self, p1name, p1odds, p1winstatus, p2name, p2odds, p2winstatus, adj_p1winstreak, adj_p2winstreak, adj_p1_tier, adj_p2_tier, p1mu, p1sigma, p2mu, p2sigma, match_time, bet_outcome, is_tourney):  
            
            # NOTE: *******DO NOT FORGET TO ALSO CHANGE get_most_recent() WITH UPDATED KEYS YOU ADD/REMOVE FROM THE LIST ON THE LINE BELOW THIS ONE:*******

            sql = 'INSERT INTO SBMATCHES (p1name, p1odds, p1win, p1streak, p1mu, p1sigma, p1tier, p1tourney, p1time, p2name, p2odds, p2win, p2streak, p2mu, p2sigma, p2tier, p2tourney, p2time, betOutcome) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            data = [
            (p1name, p1odds, p1winstatus, adj_p1winstreak, p1mu, p1sigma, adj_p1_tier, is_tourney, match_time, p2name, p2odds, p2winstatus, adj_p2winstreak, p2mu, p2sigma, adj_p2_tier, is_tourney, match_time, bet_outcome,)
            ]
            
            if all(variables is not None for variables in [adj_p1winstreak, adj_p2winstreak, adj_p1_tier, adj_p2_tier]): # If both adjusted-player-winstreaks and adjusted-tier come back successfully, record the match.
                try:
                    with self.con:
                        self.con.executemany(sql, data)
                        self.con.commit()
                        print(f"This match has been added to the DB. There are now {self.num_from_db()} records in the database.")
                        self.make_backup()
                        # self.get_win_avg()
                except sqlite3.IntegrityError:
                    print("This match already exists in the DB.")               
            else:
                print("Either winstreaks or tier didn't retrieve.  This match wasn't recorded.")
                      
        def update_match(self):  # Updates a match in the table. 
            with self.con:
                self.con.execute("UPDATE SBMATCHES set p1win = 'TEST_STRING' WHERE p1win = 'locked'")
                self.con.commit()

        def delete_match(self):  # Deletes a match from the table (leaves blank row).
            with self.con:
                self.con.execute("DELETE from SBMATCHES where ID <= 1000;")
                print("Total number of rows deleted:", self.con.total_changes)

        def get_win_avg(self): # Gets the average percentage of bets you've won.  (NOTE:  Actual probability betting started at match ID 250.)
            with self.con:
                data = self.con.execute("""SELECT avg(bet_outcome) FROM SBMATCHES;""")
                avg_bet = data.fetchall()
            print(avg_bet[0][0])

        def db_for_pandas(self):  # Selects and prints out entire table
            with self.con:
                data = self.con.execute("SELECT * from SBMATCHES")
                for row in data:
                    # print(row)
                    yield row

        def num_from_db(self):  # Selects and prints out number of records in DB.
            with self.con:
                data = self.con.execute(f"""SELECT max(id) FROM SBMATCHES;""")
                maxID = data.fetchall()
            return maxID[0][0]          

        def make_backup(self):
            self.match_count += 1
            if self.match_count % 10 == 0:
                with self.backup_con:
                    self.con.backup(self.backup_con)              
                print("Successful DB Backup!")

        def get_winstreaks_from_DB(self, player_search):
            db_winstreak = None
            if self.get_most_recent(player_search) == None:
                db_winstreak = None
            elif self.get_most_recent(player_search)[0]['p1name'] == player_search:
                db_winstreak = self.get_most_recent(player_search)[0]['p1streak']
            elif self.get_most_recent(player_search)[0]['p2name'] == player_search:
                db_winstreak = self.get_most_recent(player_search)[0]['p2streak']
            return db_winstreak
                    
        def get_ratings_from_DB(self, player_search):  # Gets the Mu and Sigma from the latest match, if a match exists.  # NOTE:  Can return None. (None = Default Ratings will be assigned from Bettor later.)
            if (self.get_most_recent(player_search) == []) or (self.get_most_recent(player_search) == None):
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
                    data = self.con.execute(f"""SELECT *, max(id) as latest FROM SBMATCHES WHERE p1name = ("{player_search}") OR p2name = ("{player_search}");""")
                    most_recent = data.fetchall()                                
                keys = ["id", "p1name", "p1odds", "p1win", "p1streak", "p1mu", "p1sigma", "p1tier", "p1tourney", "p1time", "p2name", "p2odds", "p2win", "p2streak", "p2mu", "p2sigma", "p2tier", "p2tourney", "p2time", "bet_outcome"]
                dict_list = []
                for i in range(len(most_recent)):
                    dict_list.append(dict(zip(keys, most_recent[i])))
                return dict_list  # Returns either an empty list, or a list of 1 dictionary containing the latest match for specified player.
            
        def get_player_matches(self, player_search):  # Gathers ALL games of a selected player from the DB .  
            with self.con:
                data = self.con.execute(f"""SELECT * FROM SBMATCHES WHERE p1name = ("{player_search}") OR p2name = ("{player_search}");""")
                all_games= data.fetchall()  # TODO: Maybe replace the single quotes, and double quotes, with escaped quotes:  ex:  player_search.replace('"', '\"')}")
                return all_games # Returns either an empty list, or a list of tuples of all matches, with each tuple containing 1 match.
