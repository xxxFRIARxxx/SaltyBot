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

    def record_match(self, p1name, p1odds, p1winstatus, p2name, p2odds, p2winstatus, adj_p1winstreak, adj_p2winstreak,
                     adj_p1_tier, adj_p2_tier, p1mu, p1sigma, p2mu, p2sigma, match_time, bet_outcome, is_tourney):

        data = [
            (p1name, p1odds, p1winstatus, adj_p1winstreak, p1mu, p1sigma, adj_p1_tier, is_tourney, match_time, p2name,
             p2odds, p2winstatus, adj_p2winstreak, p2mu, p2sigma, adj_p2_tier, is_tourney, match_time, bet_outcome,)
        ]

        if all(variables is not None for variables in [adj_p1winstreak, adj_p2winstreak, adj_p1_tier, adj_p2_tier]):

            sql = 'INSERT INTO SBMATCHES (p1name, p1odds, p1win, p1streak, p1mu, p1sigma, p1tier, p1tourney, p1time, ' \
                  'p2name, p2odds, p2win, p2streak, p2mu, p2sigma, p2tier, p2tourney, p2time, betOutcome) values (?, ' \
                  '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
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
            print("Either winstreaks or tier didn't retrieve from Twitch.  This match wasn't recorded.")

    def update_match(self):  # Updates a match in the table.
        with self.con:
            self.con.execute("UPDATE SBMATCHES set p1win = 'TEST_STRING' WHERE p1win = 'locked'")
            self.con.commit()

    def delete_match(self):  # Deletes a match from the table (leaves blank row).
        with self.con:
            self.con.execute("DELETE from SBMATCHES where ID <= 1000;")
            print("Total number of rows deleted:", self.con.total_changes)

    def get_odds_average(self, player_search):  # Gets the average of a fighter's odds from the DB
        if not self.get_all_matches(player_search):
            return 1
        with self.con:
            oddsfromDB_p1 = self.con.execute(
                f"""SELECT p1odds FROM SBMATCHES WHERE p1name = ("{player_search}");""")
            oddsfromDB_p2 = self.con.execute(
                f"""SELECT p2odds FROM SBMATCHES WHERE p2name = ("{player_search}");""")
            p1_oddsfromDB, p2_oddsfromDB = oddsfromDB_p1.fetchall(), oddsfromDB_p2.fetchall()
        odds_list = [i[0] for i in p1_oddsfromDB]
        odds_list.extend(j[0] for j in p2_oddsfromDB)
        return sum(odds_list) / len(odds_list)

    def get_win_avg(self):  # Gets the average percentage of bets you've won.
        with self.con:
            data = self.con.execute("""SELECT avg(bet_outcome) FROM SBMATCHES;""")
            avg_bet = data.fetchall()
        print(avg_bet[0][0])

    def db_for_pandas(self):  # Selects and prints out entire table
        with self.con:
            yield from self.con.execute("SELECT * from SBMATCHES")

    def recent_for_pandas(self, player_search):
        with self.con:
            yield from self.most_recent_match(player_search)

    def num_from_db(self):  # Selects and prints out number of records in DB.
        with self.con:
            data = self.con.execute("""SELECT max(id) FROM SBMATCHES;""")
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
        if self.most_recent_match(player_search) is None:
            db_winstreak = None
        elif self.most_recent_match(player_search)[0]['p1name'] == player_search:
            db_winstreak = self.most_recent_match(player_search)[0]['p1streak']
        elif self.most_recent_match(player_search)[0]['p2name'] == player_search:
            db_winstreak = self.most_recent_match(player_search)[0]['p2streak']
        return db_winstreak

    def get_ratings_from_DB(self, player_search):
        if (self.most_recent_match(player_search) == []) or (self.most_recent_match(player_search) is None):
            player_mu = None
            player_sigma = None
        elif self.most_recent_match(player_search)[0]['p1name'] == player_search:
            player_mu = self.most_recent_match(player_search)[0]['p1mu']
            player_sigma = self.most_recent_match(player_search)[0]['p1sigma']
        elif self.most_recent_match(player_search)[0]['p2name'] == player_search:
            player_mu = self.most_recent_match(player_search)[0]['p2mu']
            player_sigma = self.most_recent_match(player_search)[0]['p2sigma']
        return player_mu, player_sigma

    def most_recent_match(self, player_search):
        if self.get_all_matches(player_search):
            with self.con:
                data = self.con.execute(
                    f"""SELECT *, max(id) as latest FROM SBMATCHES WHERE p1name = ("{player_search}") OR p2name = ("{player_search}");""")
                most_recent = data.fetchall()
            keys = ["id", "p1name", "p1odds", "p1win", "p1streak", "p1mu", "p1sigma", "p1tier", "p1tourney", "p1time",
                    "p2name", "p2odds", "p2win", "p2streak", "p2mu", "p2sigma", "p2tier", "p2tourney", "p2time",
                    "betOutcome"]
            return [dict(zip(keys, most_recent[i])) for i in range(len(most_recent))]

    def get_all_matches(self, player_search):
        with self.con:
            data = self.con.execute(
                f"""SELECT * FROM SBMATCHES WHERE p1name = ("{player_search}") OR p2name = ("{player_search}");""")
            return data.fetchall()
