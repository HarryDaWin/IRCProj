"""To run this code you need python install and run the command py irc-server.py to start the server. To run the client
you need to up another terminal and run py irc-client.py"""

import socket


class IRCClient:
    def __init__(self, host='127.0.0.1', port=6667):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
       
    def check_message(self, message, user):
        if len(message) > 4:
            print("Wrong command try using HELP to find correct commands")
            return True

        #Client creates a room
        if message == 'CREA':
            room_name = input("Type in the room name you wish to create: ")
            self.sock.send(f"{message} {room_name}\r\n".encode())
            return True
        
        #Leave a room

        elif message == 'PART':
            self.sock.send(f"LIST".encode())
            resp = self.sock.recv(1000000).decode()
            print(resp)
            room_name = input("Type in the room name you wish to leave: ")
            self.sock.send(f"{message} {room_name}\r\n".encode())
            return True
        
        #send a message to room
        elif message == 'MESG':
            self.sock.send(f"LIST".encode())
            resp = self.sock.recv(1000000).decode()
            print(resp)
            #takes in room they wish to message
            room_name = input("Type in the room/rooms name you wish to message(ex: room1): ")
            msg = input("Type in the message you wish to send: ")
            #sends the command , user, roomname, msg for the server to interpret
            self.sock.send(f"{message} {room_name} {user} {msg}\r\n".encode())
            return True
        
        elif message == 'DMSG':
            self.sock.send(f"LIST".encode())
            resp = self.sock.recv(1000000).decode()
            print(resp)
            rooms = input("Type in the rooms you wish to send distinct messages to (ex. room1 room2): ")
            params = rooms.strip().split()
            for room_name in params:
                msg = input(f"Type in the message you wish to send {room_name}: ")
                self.sock.send(f"MESG {room_name} {user} {msg}\r\n".encode())
            return True
                    
        elif message == 'MSGB':
            self.sock.send(f"LIST".encode())
            resp = self.sock.recv(1000000).decode()
            print(resp)
            room_name = input("Type in the room you wish to messages for: ")
            self.sock.send(f"{message} {room_name}\r\n".encode())
            return True

        #Client can join a room
        elif message == 'JOIN':
            self.sock.send(f"LIST".encode())
            resp = self.sock.recv(1000000).decode()
            print(resp)
            #takes in room or rooms in a space seperated
            room_name = input("Type in the room/rooms name you wish to join(ex: room1 room2 room3): ")
            self.sock.send(f"{message} {user} {room_name} \r\n".encode())
            return True
        
        #client can list all members in the room
        elif message == 'MEMB':
            self.sock.send(f"LIST".encode())
            resp = self.sock.recv(1000000).decode()
            print(resp)
            room_name = input("Type in the room name you wish to see all members: ")
            self.sock.send(f"{message} {room_name} \r\n".encode())
            return True
        
        elif message == 'DISC':
            self.sock.send(f"{message}".encode())
            resp = self.sock.recv(1000000).decode()
            print(resp)
            return False
        
        elif message == 'HELP':
            print("""
                MESG = message a room
                MSGB = see message thread in room
                DMSG = send distinct messages to multiple (selected) rooms
                CREA = create room
                JOIN = join room
                PART = leave room
                LIST = list rooms
                MEMB = List members in the room
                DISC = disconnect from server
                """)
        
        #if client uses LIST then it comes down and runs here
        else:
            self.sock.send(f"{message}".encode())
        return True




if __name__ == "__main__":
    #variable for the loop to keep on running
    q = True
    #object for client to connect to the host
    client = IRCClient()
    print("You have successfully connected to the server")
    #asking user for a username
    user = input("Type in the username you wish to use: ")
    while q:
        try: 
            #grabbing a command to be process
            msg = input("What command would you like to do: ")
            q = client.check_message(msg, user)
            client.sock.settimeout(3.0) # Timeout after 5 seconds

            while True:
                try:
                    resp = client.sock.recv(1000000).decode()
                    if resp: # Check if the response is not empty
                        print(resp)
                    else:
                        break # Exit the loop if the response is empty
                except socket.timeout:
                    print("Timeout reached, Received all Data.")
                    break # Exit the loop if a timeout occurs
                #if server crashes
        except socket.error as e:
            print(f"An error occurred: {e}")
            #  exit gracefully
            q = False


