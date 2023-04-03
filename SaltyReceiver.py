from SaltySocket import SaltySocket
import re
import threading
from alive_progress import alive_bar

class CustomThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = SaltySocket()
        self.true_p1_streak = None
        self.true_p2_streak = None
        self.true_tier = None
 
    def run(self):
        self.sock.open_socket() 
        self.sock.send_ping()
        with alive_bar(title="Working...",spinner=None,enrich_print=False, length=15, unknown="dots_waves", stats=False, elapsed=False, monitor=False):  
            while True:
                run_message = self.sock.read_message()
                if run_message != None:
                    if (run_message.startswith(":waifu4u!")): 
                        if (run_message.find('Bets are locked.')) != -1:
                            response_message = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', run_message)[0]  # Find the message from waifu
                            res = re.findall(r"\(\s*\+?(-?\d+)\s*\)", response_message)  # Parse the message from waifu in to winstreaksk
                            self.sock.find_winstreak = False
                            try:
                                self.true_p1_streak = int(res[0])
                                self.true_p2_streak = int(res[1])
                            except:
                                self.true_p1_streak = None
                                self.true_p2_streak = None
                            print(f"True Streaks are: {self.true_p1_streak, self.true_p2_streak}")
                        elif (run_message.find("Bets are OPEN")) != -1: 
                            response_message = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', run_message)[0]  # Find the message from waifu
                            tier_res = re.findall(r"\((.){1} Tier\)", response_message)  # Parse the message from waifu in to tier
                            try:
                                for index, item in enumerate(["P","B","A","S","X"], 1):
                                    if tier_res[0] in item:
                                        self.true_tier = index
                                        break                        
                                    else:
                                        self.true_tier = None
                            except IndexError:
                                self.true_tier = None
                            finally:
                                print(f"Current Tier is: {self.true_tier}")      
                # TODO: Set timer snapshot here, and set all proper flags to move to recording, and the next stage.
                
                # elif (run_message.startswith(":saltybet!")):
                #     if (run_message.find("Exhibitions will start shortly.") != -1):
                #         response_message = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', run_message)[0]  # Find the message from SaltyBet