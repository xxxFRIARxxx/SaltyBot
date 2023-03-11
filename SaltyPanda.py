import pandas

class SaltyPanda():
    def __init__(self):
        self.db_list = None
        self.data_frame = self.data_frame = pandas.DataFrame(self.db_list, columns =["ID","p1name", "p1odds", "p1win", "p1streak", "p1mu", "p1sigma", "p1tier", "p1tourney", "p1time", "p2name", "p2odds", "p2win", "p2streak", "p2mu", "p2sigma", "p2tier", "p2tourney", "p2time", "betOutcome"])
        self.match_count = 0

    def dataframe_from_DB(self,db_list):
        self.db_list = list(db_list)
        self.data_frame = pandas.DataFrame(self.db_list, columns =["ID","p1name", "p1odds", "p1win", "p1streak", "p1mu", "p1sigma", "p1tier", "p1tourney", "p1time", "p2name", "p2odds", "p2win", "p2streak", "p2mu", "p2sigma", "p2tier", "p2tourney", "p2time", "betOutcome"])
        return self.data_frame
    
    def panda_to_csv(self, db_list):
        self.match_count += 1
        self.db_list = list(db_list)
        self.data_frame = pandas.DataFrame(self.db_list, columns =["ID","p1name", "p1odds", "p1win", "p1streak", "p1mu", "p1sigma", "p1tier", "p1tourney", "p1time", "p2name", "p2odds", "p2win", "p2streak", "p2mu", "p2sigma", "p2tier", "p2tourney", "p2time", "betOutcome"])
        if self.match_count % 10 == 0:
            pandas.DataFrame.to_csv(self.data_frame, "SaltyCSV.csv", index=False)
            print("CSV Made!")

    def print_pandas(self):
        print(self.db_list) 
        print(self.data_frame) 
        