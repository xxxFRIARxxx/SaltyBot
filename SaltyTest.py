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
            print(run_message)

test = CustomThread()

test.start()

