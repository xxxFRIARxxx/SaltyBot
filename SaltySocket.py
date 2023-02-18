import socket
import re
import threading

# FUCK SOCKETS.  ALL MY HOMIES HATE SOCKETS.

connection_data = ('irc.chat.twitch.tv', 6667)
token = "oauth:ljm74i4rbiqkkt66hw6738rpzezrei"
user = "AUTO__SAVE"
channel = "#saltybet"
readbuffer = ""


class SaltySocket():
    def __init__(self):        

        #  Removed connecting the socket on instantiation due to need for more precise control of sockets.
        #  Must now open_socket(), read_message() (in while loop), and break message loops individually.  Socket is never closed.  Instead, PING is spammed to server every 20 sec.
        self.find_winstreak = False
        self.p1winstreak = None
        self.p2winstreak = None
        self.tier_res_conv = None

    def open_socket(self):  
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((connection_data[0], connection_data[1]))
        self.send_message(f"PASS {token}\r\n")
        self.send_message(f"NICK {user}\r\n")
        self.send_message(f"JOIN {channel}\r\n")

    def close_socket(self):
        self.socket.close()

    def send_message(self, constructor_message=''):
        self.socket.send(constructor_message.encode('utf-8'))  

    def read_message(self):
            message = self.socket.recv(4096).decode('utf-8')
            self.is_ping(message)
            return message

    def is_ping(self, ping_message=''):
        if ping_message.startswith("PING"):
            self.send_message("PONG :tmi.twitch.tv\r\n")
    
    def send_ping(self):
        self.socket.send("PING :tmi.twitch.tv\r\n".encode('utf-8'))
        threading.Timer(20, self.send_ping).start()

    def get_winstreaks(self):
        if (self.find_winstreak == True):        
            while True:
                run_message = self.read_message() # While called, read twitch socket.  (NEEDS to BREAK out of loop - Socket open 24/7.)
                if (run_message.startswith(":waifu4u!")): 
                    if (run_message.find('Bets are locked.')) != -1:
                        # response_username =  re.findall(r'^:([a-zA-Z0-9_]+)!', run_message)[0]
                        response_message = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', run_message)[0]  # Find the message from waifu
                        res = re.findall(r"\(\s*\+?(-?\d+)\s*\)", response_message)  # Parse the message from waifu in to winstreaksk
                        self.find_winstreak = False
                        try:
                            self.p1winstreak = int(res[0])
                            self.p2winstreak = int(res[1])
                        except:
                            self.p1winstreak = None
                            self.p2winstreak = None
                        break
                    elif (run_message.find('Payouts')) != -1:
                        self.find_winstreak = False
                        self.p1winstreak = None
                        self.p2winstreak = None
                        break
    
    def get_tier(self):
        while True:
            run_message = self.read_message() # While called, read twitch socket.  (NEEDS to BREAK out of loop - Socket open 24/7.)
            if (run_message.startswith(":waifu4u!")):
                if (run_message.find("Bets are OPEN")) != -1:
                # response_username =  re.findall(r'^:([a-zA-Z0-9_]+)!', run_message)[0]
                    response_message = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', run_message)[0]  # Find the message from waifu
                    tier_res = re.findall(r"\((.){1} Tier\)", response_message)  # Parse the message from waifu in to tier
                    if tier_res[0] == "P":
                        self.tier_res_conv = 1
                    elif tier_res[0] == "B":
                        self.tier_res_conv = 2
                    elif tier_res[0] == "A":
                        self.tier_res_conv = 3
                    elif tier_res[0] == "S":
                        self.tier_res_conv = 4
                    elif tier_res[0] == "X":
                        self.tier_res_conv = 5
                    else:
                        print(tier_res[0])
                        self.tier_res_conv = None
                    break              
                elif (run_message.find('Bets are locked')) != -1:
                    self.tier_res_conv = None
                    break              
        print(f"Current Tier is: {self.tier_res_conv}")
        return self.tier_res_conv

# TODO: WINSTREAK:
# TODO: Talk to Craig about why he wants to (and is in the middle of) removing adj_winstreak and going back to p1winstreak and p2winstreak in recorder.
# TODO: If winstreak is < -15, or > 15 set winstreak to 1 (Only if you implement character tiers)