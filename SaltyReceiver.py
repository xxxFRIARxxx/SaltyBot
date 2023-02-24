from SaltySocket import SaltySocket
import re
import threading

class CustomThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = SaltySocket()
        self.value1 = None
        self.value2 = None
        self.value3 = None
 
    def run(self):
        self.sock.open_socket() 
        self.sock.send_ping()  
        while True:
            run_message = self.sock.read_message() 
            if (run_message.startswith(":waifu4u!")): 
                if (run_message.find('Bets are locked.')) != -1:
                    response_message = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', run_message)[0]  # Find the message from waifu
                    res = re.findall(r"\(\s*\+?(-?\d+)\s*\)", response_message)  # Parse the message from waifu in to winstreaksk
                    self.sock.find_winstreak = False
                    try:
                        self.value1 = int(res[0])
                        self.value2 = int(res[1])
                    except:
                        self.value1 = None
                        self.value2 = None
                    print(f"Winstreaks are: {self.value1, self.value2}")
                elif (run_message.find("Bets are OPEN")) != -1: 
                    response_message = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', run_message)[0]  # Find the message from waifu
                    tier_res = re.findall(r"\((.){1} Tier\)", response_message)  # Parse the message from waifu in to tier
                    if tier_res[0] == "P":
                        self.value3 = 1
                    elif tier_res[0] == "B":
                        self.value3 = 2
                    elif tier_res[0] == "A":
                        self.value3 = 3
                    elif tier_res[0] == "S":
                        self.value3 = 4
                    elif tier_res[0] == "X":
                        self.value3 = 5
                    else:
                        print(tier_res[0])
                        self.value3 = None            
                    print(f"Current Tier is: {self.value3}")