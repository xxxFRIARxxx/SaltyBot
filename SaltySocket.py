import socket
import threading
import time
import os

connection_data = ('irc.chat.twitch.tv', 6667)
channel = "#saltybet"

class SaltySocket():
    def __init__(self):
        self.find_winstreak = False
        self.p1winstreak = None
        self.p2winstreak = None
        self.tier_res_conv = None
        

    def open_socket(self):  
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((connection_data[0], connection_data[1]))
        self.send_message(f"PASS {os.getenv('token')}\r\n")
        self.send_message(f"NICK {os.getenv('user')}\r\n")
        self.send_message(f"JOIN {channel}\r\n")

    def close_socket(self):
        self.socket.close()

    def send_message(self, constructor_message: str):
        self.socket.send((constructor_message).encode('utf-8')) 
        
    def send_twitch_chat(self, message: str):
        self.socket.send(f"PRIVMSG {channel} :{message}\n".encode('utf-8'))
                   
    def read_message(self):
        message = None
        try:
            message = self.socket.recv(4096).decode('utf-8')
        except ConnectionAbortedError:
            time.sleep(2)
            self.open_socket()
        except ConnectionResetError:
            time.sleep(2)
            self.open_socket()
        self.is_ping(message)
        return message

    def is_ping(self, ping_message=''):
        try:
            if ping_message.startswith("PING"):
                self.send_message("PONG :tmi.twitch.tv\r\n")

        except AttributeError:
            time.sleep(2)
            self.is_ping()
    def send_ping(self):
        try:
            self.socket.send("PING :tmi.twitch.tv\r\n".encode('utf-8'))
        except ConnectionResetError:
            time.sleep(3)
            self.open_socket()
        except ConnectionAbortedError:
            time.sleep(3)
            self.open_socket()
        threading.Timer(20, self.send_ping).start()
    
    def adjust_winstreak(self, p1win_status, p2win_status, p1winstreak, p2winstreak):
        self.adj_p1winstreak = p1winstreak
        self.adj_p2winstreak = p2winstreak
        if (self.adj_p1winstreak is None) or (self.adj_p2winstreak is None):
            pass
        elif (self.adj_p1winstreak <= 0) and (p1win_status == 1):
            self.adj_p1winstreak = 1
        elif (self.adj_p1winstreak <= 0) and (p1win_status == 0):
            self.adj_p1winstreak = (self.adj_p1winstreak - 1)  
        elif (self.adj_p1winstreak > 0) and (p1win_status == 1):
            self.adj_p1winstreak = (self.adj_p1winstreak + 1) 
        elif (self.adj_p1winstreak > 0) and (p1win_status == 0):
            self.adj_p1winstreak = -1
        else:
            print("This prints if P1 winstreak hasn't been adjusted for some reason.")

        if (self.adj_p1winstreak is None) or (self.adj_p2winstreak is None):
            pass
        elif (self.adj_p2winstreak <= 0) and (p2win_status == 1):
            self.adj_p2winstreak = 1
        elif (self.adj_p2winstreak <= 0) and (p2win_status == 0):
            self.adj_p2winstreak = (self.adj_p2winstreak - 1)       
        elif (self.adj_p2winstreak > 0) and (p2win_status == 1):
            self.adj_p2winstreak = (self.adj_p2winstreak + 1) 
        elif (self.adj_p2winstreak > 0) and (p2win_status == 0):
            self.adj_p2winstreak = -1
        else:
            print("This prints if P2 winstreak hasn't been adjusted for some reason.")
            
    def adjust_tier(self, tier):
        self.adj_p1_tier = tier
        self.adj_p2_tier = tier
        if (self.adj_p1winstreak is None) or (self.adj_p1_tier is None):
            pass    
        elif tier == 1:
            if self.adj_p1winstreak > 15:
                self.adj_p1winstreak == 0
                self.adj_p1_tier = 2
        elif tier == 2:
            if self.adj_p1winstreak < -15:
                self.adj_p1winstreak = 0
                self.adj_p1_tier = 1
            elif self.adj_p1winstreak > 15:
                self.adj_p1winstreak = 0
                self.adj_p1_tier = 3
        elif tier == 3:
            if self.adj_p1winstreak < -15:
                self.adj_p1winstreak = 0
                self.adj_p1_tier = 2
            elif self.adj_p1winstreak > 15:
                self.adj_p1winstreak = 0
                self.adj_p1_tier = 4
        elif tier == 4:
            if self.adj_p1winstreak < -15:
                self.adj_p1winstreak = 0
                self.adj_p1_tier = 3
        elif tier == 5:
            pass
        else:
            print("This prints if P1 tier hasn't been adjusted for some reason.")
            
        if (self.adj_p2winstreak is None) or (self.adj_p2_tier is None):
            pass       
        elif tier == 1:
            if self.adj_p2winstreak > 15:
                self.adj_p2winstreak == 0
                self.adj_p2_tier = 2
        elif tier == 2:
            if self.adj_p2winstreak < -15:
                self.adj_p2winstreak = 0
                self.adj_p2_tier = 1
            elif self.adj_p2winstreak > 15:
                self.adj_p2winstreak = 0
                self.adj_p2_tier = 3
        elif tier == 3:
            if self.adj_p2winstreak < -15:
                self.adj_p2winstreak = 0
                self.adj_p2_tier = 2
            elif self.adj_p2winstreak > 15:
                self.adj_p2winstreak = 0
                self.adj_p2_tier = 4
        elif tier == 4:
            if self.adj_p2winstreak < -15:
                self.adj_p2winstreak = 0
                self.adj_p2_tier = 3
        elif tier == 5:
            pass
        else:
            print("This prints if P2 tier hasn't been adjusted for some reason.")