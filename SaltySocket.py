import socket
import re
import threading
import time

connection_data = ('irc.chat.twitch.tv', 6667)
token = "oauth:ljm74i4rbiqkkt66hw6738rpzezrei"
user = "AUTO__SAVE"
channel = "#saltybet"
readbuffer = ""

class SaltySocket():
    def __init__(self): #  Must now open_socket(), read_message() (in while loop), and break message loops individually.  Socket is never closed.  Instead, PING is spammed to server every 20 sec.
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
        message = None
        try:
            message = self.socket.recv(4096).decode('utf-8')
        except ConnectionAbortedError:
            time.sleep(3)
            self.open_socket()
        self.is_ping(message)
        return message

    def is_ping(self, ping_message=''):
        if ping_message.startswith("PING"):
            self.send_message("PONG :tmi.twitch.tv\r\n")
    
    def send_ping(self):
        try:
            self.socket.send("PING :tmi.twitch.tv\r\n".encode('utf-8'))
        except ConnectionResetError:
            time.sleep(3)
            self.open_socket()
            # self.send_ping()  TODO: Do I need this here?  Does the thread stay open and keep trying to send pings even if the socket is closed by remote host?
        except ConnectionAbortedError:
            time.sleep(3)
            self.open_socket()
            # self.send_ping()  TODO: Do I need this here?  Does the thread stay open and keep trying to send pings even if the socket is closed by remote host?
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
    
    def adjust_winstreak(self, p1win_status, p2win_status):
        self.adj_p1winstreak = self.p1winstreak
        self.adj_p2winstreak = self.p2winstreak
        if (self.adj_p1winstreak == None) or (self.adj_p2winstreak == None):
            pass
        elif (self.adj_p1winstreak <= 0) and (p1win_status == 1):
            self.adj_p1winstreak = 1
        elif (self.adj_p1winstreak <= 0) and (p1win_status == 0):
            self.adj_p1winstreak = (self.adj_p1winstreak - 1)  
        elif (self.adj_p1winstreak >= 0) and (p1win_status == 1):
            self.adj_p1winstreak = (self.adj_p1winstreak + 1) 
        elif (self.adj_p1winstreak >= 0) and (p1win_status == 0):
            self.adj_p1winstreak = -1
        else:
            print("This prints if P1 winstreak hasn't been adjusted for some reason.")

        if (self.adj_p1winstreak == None) or (self.adj_p2winstreak == None):
            pass
        elif (self.adj_p2winstreak <= 0) and (p2win_status == 1):
            self.adj_p2winstreak = 1
        elif (self.adj_p2winstreak <= 0) and (p2win_status == 0):
            self.adj_p2winstreak = (self.adj_p2winstreak - 1)       
        elif (self.adj_p2winstreak >= 0) and (p2win_status == 1):
            self.adj_p2winstreak = (self.adj_p2winstreak + 1) 
        elif (self.adj_p2winstreak >= 0) and (p2win_status == 0):
            self.adj_p2winstreak = -1
        else:
            print("This prints if P2 winstreak hasn't been adjusted for some reason.")
            
    def adjust_tier(self):
        self.adj_p1_tier = self.tier_res_conv
        self.adj_p2_tier = self.tier_res_conv
        if (self.adj_p1winstreak == None) or (self.adj_p1_tier == None):
            pass    
        elif self.tier_res_conv == 1:
            if self.adj_p1winstreak > 15:
                self.adj_p1winstreak == 1
                self.adj_p1_tier = 2
        elif self.tier_res_conv == 2:
            if self.adj_p1winstreak < -15:
                self.adj_p1winstreak = 1
                self.adj_p1_tier = 1
            elif self.adj_p1winstreak > 15:
                self.adj_p1winstreak = 1
                self.adj_p1_tier = 3
        elif self.tier_res_conv == 3:
            if self.adj_p1winstreak < -15:
                self.adj_p1winstreak = 1
                self.adj_p1_tier = 2
            elif self.adj_p1winstreak > 15:
                self.adj_p1winstreak = 1
                self.adj_p1_tier = 4
        elif self.tier_res_conv == 4:
            if self.adj_p1winstreak < -15:
                self.adj_p1winstreak = 1
                self.adj_p1_tier = 3
        elif self.tier_res_conv == 5:
            pass
        else:
            print("This prints if P1 tier hasn't been adjusted for some reason.")
            
        if (self.adj_p2winstreak == None) or (self.adj_p2_tier == None):
            pass       
        elif self.tier_res_conv == 1:
            if self.adj_p2winstreak > 15:
                self.adj_p2winstreak == 1
                self.adj_p2_tier = 2
        elif self.tier_res_conv == 2:
            if self.adj_p2winstreak < -15:
                self.adj_p2winstreak = 1
                self.adj_p2_tier = 1
            elif self.adj_p2winstreak > 15:
                self.adj_p2winstreak = 1
                self.adj_p2_tier = 3
        elif self.tier_res_conv == 3:
            if self.adj_p2winstreak < -15:
                self.adj_p2winstreak = 1
                self.adj_p2_tier = 2
            elif self.adj_p2winstreak > 15:
                self.adj_p2winstreak = 1
                self.adj_p2_tier = 4
        elif self.tier_res_conv == 4:
            if self.adj_p2winstreak < -15:
                self.adj_p2winstreak = 1
                self.adj_p2_tier = 3
        elif self.tier_res_conv == 5:
            pass
        else:
            print("This prints if P2 tier hasn't been adjusted for some reason.")