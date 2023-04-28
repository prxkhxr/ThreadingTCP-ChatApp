import socket

def ChatRoomInterface(socket : socket.socket):
    print("0 : Read messages")
    print("1 : Send message")
    print("2 : Leave")

    choice = int(input("Enter your choice : "))

    global chat_joined

    if choice == 0:
        print()
        try:
            while True:
                print(socket.recv(1024).decode()) 
        except KeyboardInterrupt:
            print("Going to previous screen")

    elif choice == 1:
        print()
        msg = input("Message : ")
        send_command(socket, f"send {msg}")

    elif choice == 2:
        send_command(socket, "leave chat")
        socket.settimeout(0.001)
        try:
            while True:
                socket.recv(1024).decode()
        except:
            print("Chatroom left successfully.")

        socket.settimeout(None)

        chat_joined = False




def LoggedInInterface(socket : socket.socket):
    print("0 : join a chat room")
    print("1 : create a chat room")
    print("2 : logout")

    choice = int(input("Enter your choice : "))
    
    global logged_in
    global chat_joined

    if choice == 2:
        send_command(socket, "logout user")
        reply = socket.recv(1024).decode()
        print(reply)
        logged_in = False
    
    elif choice == 0:
        room_name = input("Enter Chat Room name to join : ")
        
        send_command(socket, f"join {room_name}")
        reply = socket.recv(1024).decode()
        print(reply)

        if reply[0] == 'J':
            chat_joined = True
    
    elif choice == 1:
        room_name = input("Enter Chat Room name : ")

        send_command(socket, f"create {room_name}")
        reply = socket.recv(1024).decode()
        print(reply)

        if reply[0] == "C":
            chat_joined = True


def MainInterface(socket : socket.socket):
    print("0 : register")
    print("1 : login")
    print("2 : exit")

    choice = int(input("Enter your choice : "))

    global running
    global logged_in

    userID = ""
    passwd = ""

    if choice == 0:
        userID = input("Enter username : ")
        passwd = input("Enter password : ")

        send_command(socket, f"register {userID} {passwd}")
        reply = socket.recv(1024).decode()
        print(reply)

    elif choice == 1:
        userID = input("Enter username : ")
        passwd = input("Enter password : ")

        send_command(socket, f"login {userID} {passwd}")
        reply = socket.recv(1024).decode()
        print(reply)

        if reply[0] == 'L':
            send_command(socket, "received")
            print("-------------------------Active-Users-------------------------")
            l_active = [x.strip("\'") for x in socket.recv(1024).decode().strip().lstrip('[').rstrip(']').split(', ')]
            print(', '.join(l_active))
            print("--------------------------------------------------------------")
            logged_in = True
    
    elif choice == 2:
        running = False
        send_command(socket, "exit application")
    

def send_command(socket : socket.socket, msg : str):
    msg += "\n"
    socket.send(msg.encode())

if __name__ == "__main__":

    server_addr = "127.0.0.1"
    server_port = 8888

    csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    csock.connect((server_addr, server_port))

    print("----------------------------------------------------------------------------")
    print("Welcome to Client-Server Chat Application")
    print("----------------------------------------------------------------------------")

    logged_in = False
    running = True
    chat_joined = False

    while running:

        if logged_in:
            if chat_joined:
                ChatRoomInterface(csock)
            else:
                LoggedInInterface(csock)
        else:
            MainInterface(csock)

    csock.close()