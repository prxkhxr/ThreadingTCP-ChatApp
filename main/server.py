import socket
import socketserver
import threading
from datetime import datetime

class ClientHandler(socketserver.StreamRequestHandler):

    def Stringread(self):
        return self.rfile.readline().decode().strip()
    
    def Stringwrite(self, msg):
        self.wfile.write(msg.encode())

    def handle(self):
        userID = None
        room_name = None
        
        while True:
            message = self.Stringread()

            command, args = message.split()[0], message.split()[1:]

            if command == "register":
                if len(args) != 2:
                    self.Stringwrite("Expected 2 arguments.\n")
                    continue
                
                if args[0] in users.keys():
                    self.Stringwrite("User already exists.\n")
                    continue
                
                user_lock.acquire()
                users[args[0]] = args[1]
                print(f"All users = {users}")
                user_lock.release()
                self.Stringwrite("User registered successfully.\n")
            
            elif command == "login":
                if len(args) != 2:
                    self.Stringwrite("Expected 2 arguments.\n")
                    continue

                if args[0] not in users.keys():
                    self.Stringwrite("User not registered.\n")
                    continue
                
                user_lock.acquire()
                if users[args[0]] == args[1]:
                    userID = args[0]
                    active_users.append(userID)
                    print(f"Acive users = {active_users}")
                    self.Stringwrite(f"Logged in successfully as UserID : {userID}\n")
                    l = self.Stringread()
                    self.Stringwrite(f'{active_users}\n')
                else:
                    self.Stringwrite(f"Incorrect credentials.\n")
                user_lock.release()

            elif command == "logout":
                
                active_users.remove(userID)

                self.Stringwrite("Logged out successfully.\n")
                active_lock.acquire()
                print(active_users)
                active_lock.release()

            elif command == "exit":
                self.request.shutdown(socket.SHUT_RDWR)
                self.request.close()
                print("Client exited")
                break
            
            elif command == "join":
                if len(args) != 1:
                    self.Stringwrite("Expected 1 argument.\n")

                chatRooms_lock.acquire()
                if args[0] not in chatRooms.keys():
                    self.Stringwrite("Room ID does not exist.\n")
                    continue
                
                room_name = args[0]

                chatRooms[room_name].add_member(userID, self.request)
                self.Stringwrite(f"Joined Room {chatRooms[room_name].name}\n")
                chatRooms[room_name].display_users()
                chatRooms_lock.release()

            elif command == "create":
                if len(args) != 1:
                    self.Stringwrite("Expected 1 argument.\n")

                if args[0] in chatRooms.keys():
                    self.Stringwrite("Room ID already exists.\n")
                
                chatRooms_lock.acquire()
                room_name = args[0]
                _room = ChatRoom(room_name)
                chatRooms[room_name] = _room
                _room.add_member(userID, self.request)
                self.Stringwrite(f"Created and Joined Room {chatRooms[room_name].name}\n")
                chatRooms[room_name].display_users()
                chatRooms_lock.release()

            elif command == "leave":
                
                chatRooms_lock.acquire()
                chatRooms[room_name].remove_member(userID)
                self.Stringwrite(f"Exited Room {chatRooms[room_name].name}\n")
                chatRooms[room_name].display_users()
                chatRooms_lock.release()

            
            elif command == "send":
                msg = ' '.join(args)

                chatRooms_lock.acquire()
                d = chatRooms[room_name].chat_active_members
                for i in d.values():
                    i.send(f"{datetime.now().strftime('%I:%M:%S:%p')} {userID} : {msg}\n".encode())
                chatRooms_lock.release()





                


class ChatRoom:

    def __init__(self, name) -> None:
        self.name = name
        self.message = {}
        self.chat_active_members = {}

    def add_member(self, userID, client_socket):
        self.chat_active_members[userID] = client_socket
        return 1

    def remove_member(self, userID):
        del self.chat_active_members[userID]
        return 1
    
    def display_users(self):
        print(self.chat_active_members.keys())






    

if __name__ == "__main__":

    user_lock = threading.Lock()
    active_lock = threading.Lock()
    chatRooms_lock = threading.Lock()

    users = {}
    active_users = []
    chatRooms = {}

    addr = "127.0.0.1"
    port = 8888

    
    server = socketserver.ThreadingTCPServer((addr,port), ClientHandler)

    server.serve_forever()