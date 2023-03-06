import pandas as panda
from SaltyDatabase import SaltyDatabase

db_list = list(SaltyDatabase().db_for_pandas())
data_frame = panda.DataFrame(db_list, columns =["ID","p1name", "p1odds", "p1win", "p1streak", "p1mu", "p1sigma", "p1tier", "p1tourney", "p1time", "p2name", "p2odds", "p2win", "p2streak", "p2mu", "p2sigma", "p2tier", "p2tourney", "p2time", "betOutcome"])
 
print(data_frame) 


