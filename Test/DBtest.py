import sqlite3     
from trueskill import Rating, rate_1vs1, quality_1vs1

betStatus = '1'

class SaltySkill():
    def __init__(self):
        self.p1Rating = Rating()
        self.p2Rating = Rating()
    def get_rating(self):
        # if found in the DB, 
        pass
    def set_rating(self, betStatus):
        # print(self.p1Rating)
        # print(self.p2Rating)
        # print(type(self.p1Rating))
        if betStatus == "1":
            self.p1Rating, self.p2Rating = rate_1vs1(self.p1Rating, self.p2Rating)
            print("Player 1 wins!")
            print(f"Player 1's new rating is {self.p1Rating}.  Player 2's new rating is {self.p2Rating}")
        elif betStatus == "2":
            self.p2Rating, self.p1Rating = rate_1vs1(self.p2Rating, self.p1Rating)
            print("Player 2 wins!")
            print(f"P1 new rating is {self.p1Rating}.  Player 2's new rating is {self.p2Rating}")
        return self.p1Rating, self.p2Rating     

class SaltyRecorder(): 
    def __init__(self):
        self.con = sqlite3.connect('SaltDatabase.db')
        with self.con:
            self.con.execute("""CREATE TABLE IF NOT EXISTS CHARDB (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                p1rating TEXT
            );
        """)
     
     
     
    def record_match(self): 
        sql = 'INSERT INTO CHARDB (p1rating) values (?)'
        data = [
        (skill.set_rating('1'))
        ]
        try:
            with self.con:
                self.con.executemany(sql, data)
                self.con.commit()
                print(str(data))
                print("This record has been added to the DB")
        except sqlite3.IntegrityError:
            print("This match already exists in the DB.")

recorder = SaltyRecorder()
skill = SaltySkill()

recorder.record_match()

