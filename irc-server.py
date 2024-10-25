"""To run this code you need python install and run the command py irc-server.py to start the server. To run the client
you need to up another terminal and run py irc-client.py"""


import socket
import threading
import signal
import sys

#Helper lists for listing all rooms and members in the room
list_rooms = []
memb_list = []



#Data structure for msg
class msg():
    def __init__(self, user, msg):
        self.user = user
        self.msg = msg
    def print(self):
        return self.user + ': ' + self.msg

#Data structure for room 
class room:
    def __init__(self):
        self.name = ''
        self.members = {} # dictionary for user and links it with their socket
        self.msgs = [] #msg board

    #Check if the room name already exist
    def check(self, room_name):
        if room_name == self.name:
            return True
        return False

    #creates the room with a name binding to it
    def create_room(self, room_name):
        self.name = room_name

    #Joins a user with their name and socket 
    def join(self, client_socket, username): 
        self.members[client_socket] = username
    
    #Check if the user is already a member
    def is_member(self, client_socket):
        return client_socket in self.members

    def message(self, user, message):
        #appends a msg obj to list of msgs so messages can be seen similar to a message app
        x = msg(user, message)
        self.msgs.append(x)

    def leave(self, client_socket):
        if client_socket in self.members:
            del self.members[client_socket] # Remove the client_socket from the dictionary
    
    #returns the room name for the server to check
    def room_name(self):
        return self.name
    
    # Return a list of usernames
    def members_in_room(self):
        return list(self.members.values()) 
    
    #Returns a list of messages in the board
    def msg_board(self):
        return self.msgs


class IRCServer():
    def __init__(self, host='127.0.0.1', port=6667):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.clients = []
        self.rooms = []
    
    def handle_client(self, client_socket):
        self.clients.append(client_socket)
        try:
            while True:
                try:
                    #receive a message from the client
                    message = client_socket.recv(1024).decode()
                    if not message:
                        break # Exit the loop if the message is empty (client disconnected)
                    self.process_message(message, client_socket)
                except OSError as e:
                    if e.winerror == 10038:
                        print("Socket is not valid, client likely disconnected.")
                        break
                    else:
                        raise # Re-raise the exception if it's not the one we're expecting
        except ConnectionResetError:
            for x in self.rooms:
                x.leave(client_socket)
            print("Client disconnected unexpectedly.")
        finally:
            try:
                client_socket.close()
            except OSError as e:
                if e.winerror == 10038:
                   print("Socket already closed.")
                else:
                    raise # Re-raise the exception if it's not the one we're expecting

    def process_message(self, message, client_socket):
        """
        Commands:
        CREA = create room
        JOIN = join room
        MESG = message a room
        MSGB = see previous messages
        DMSG = send distinct messages to multiple (selected) rooms
        PART = leave room
        LIST = list rooms
        MEMB = List members in the room
        DISC = disconnect from server
        HELP = show appropriate commands
        """
        #splits the cmd line input into command str and list of params
        command, *params = message.strip().split()
        #join command for a user to join
        if command == 'JOIN':
            #Grabs the user from message
            user = params[0]
            #loops through params to find the rooms the user wishes to join
            for room_name in params[1:]:
                #Loops through rooms list
                for x in self.rooms:
                    #checks if the room name exists in rooms
                    if room_name == x.room_name():
                        #Check is the user is already in the room
                        if x.is_member(client_socket):
                            client_socket.send(f"You are already in the room: {room_name}\r\n".encode())
                            return
                        else:
                            #join the user into the room
                            x.join(client_socket, user)
                            client_socket.send(f"You have successfully joined the room: {room_name}\r\n".encode())
                            print(f"{user} just joined room: {room}")
                            break
        
        elif command == 'MESG':
            #Variables of the message sent from client
            room_name = params[0]
            user = params[1]
            #joins the message if there are any spaces in the message_text
            message_text = ' '.join(params[2:])
            #Loops through rooms list
            for x in self.rooms:
                #checks if the room name exists in rooms
                if room_name == x.room_name():
                    #checks if the user is the room if not send error
                    if client_socket in x.members:
                        x.message(user, message_text) # Add the message to the room's message board
                        client_socket.send(f"Message received successfully to {room_name}\r\n".encode())
                        print(f"A {user} just sent a message to room: {room_name}")
                        return
                    else:
                        client_socket.send(f"You are not in the room {room_name}. Cannot send message\r\n".encode())
                        return
                            
            client_socket.send(f"Room doesn't exist or incorrect format\r\n".encode())

        elif command == 'MSGB':
            room_name = params[0]
            #Loops through rooms list
            for x in self.rooms:
                #checks if the room name exists in rooms
                if room_name == x.room_name():
                    msgs = x.msg_board() # Get all messages from the room's message board
                    if not msgs: # Check if the dictionary is empty
                        client_socket.send("No messages in this room\r\n".encode())
                        return
                    else:
                        # Send all messages to the user, including the username
                        for x in msgs:
                            human_readable_msg = x.print()
                            client_socket.send(f"{human_readable_msg}\r\n".encode())
                        return
            client_socket.send(f"Room doesn't exist: {room_name}\r\n".encode())

        #Part command will leave a user in the room
        elif command == 'PART':
            room_name = params[0]
            # Find the room the user wants to leave
            for x in self.rooms:
                if room_name == x.room_name():
                    # Check if the user is in the room
                    if client_socket in x.members:
                        # Remove the user from the room
                        x.leave(client_socket)
                        # Notify the user that they have left the room
                        client_socket.send(f"You have successfully left the room: {room_name}\r\n".encode())
                        print(f"A user just left room: {room_name}")
                        return
                    else:
                        # If the user is not in the room, notify them
                        client_socket.send(f"You are not in the room: {room_name}\r\n".encode())
                        return
            # If the room doesn't exist, notify the user
            client_socket.send(f"Room doesn't exist: {room_name}\r\n".encode())

        #List all the members in the room
        elif command == 'MEMB':
            room_name = params[0]
            #Loops through the list of rooms
            for x in self.rooms:
                #Check if the room exists
                if room_name == x.room_name():
                    memb_list = list(x.members.values()) # Get all usernames from the dictionary
                    if not memb_list: # Check if the list is empty
                        client_socket.send("No members in this room".encode())
                        return
                    else:
                        client_socket.send(f"Members in the room: {', '.join(memb_list)}".encode())
                        return
            client_socket.send(f"Room doesn't exist\r\n".encode())
            
        #List all rooms avaliable 
        elif command == 'LIST':
            for x in self.rooms:
                list_rooms.append(x.room_name()) # Append each room name to list_rooms
            if not list_rooms:
                client_socket.send("No rooms have been created\r\n".encode())
            else:
                client_socket.send(f"All the rooms: {', '.join(list_rooms)}\r\n".encode())
            #clear the list room list to reset for next time
            list_rooms.clear()
        
        
        #Create a room
        elif command == 'CREA':
            room_name = params[0]
            if any(room.check(room_name) for room in self.rooms):
                client_socket.send(f"Room already exists\r\n".encode())
            else:
                # If the room doesn't exist, create it
                r = room()
                r.create_room(room_name)
                self.rooms.append(r)
                client_socket.send(f"You have successfully created {room_name}\r\n".encode())
                print("added a room")
        
        #DISC the user from the server 
        elif command == 'DISC':
            #Check if the client is in the server
            if client_socket in self.clients:
                print("removing a client from the from server")
                #Loops through all the rooms to remove the user from each room
                for x in self.rooms:
                    x.leave(client_socket)
                self.clients.remove(client_socket)
                client_socket.send(f"You have been disconnected from server: ".encode())
                client_socket.close()
            else:
                room_name("Client not found.")
        
        else:
            client_socket.send(f"Bad command".encode())
            
    def shutdown(self, signum, frame):
        print("\nGracefully shutting down from SIGINT (Ctrl-C)")
        # Close all client connections
        for client_socket in self.clients:
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
        
        # Shutdown the server socket
        self.sock.shutdown(socket.SHUT_RDWR)
        
        # Close the server socket
        self.sock.close()
        
        # Exit the program
        sys.exit(0)

    def start(self):
        signal.signal(signal.SIGINT, self.shutdown)
        while True:
            client_socket, _ = self.sock.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    server = IRCServer()
    server.start()