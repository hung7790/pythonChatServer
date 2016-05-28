# Chat server written in python
 
import socket, select


users = {}
rooms = {}
#This function is used for setting user name
def set_name(sock,message):
    try:
        for user in users.values():
            if len(users) > 0 :
                if  user[0] == message:
                    sock.send("Sorry, name taken.\r\n")
                    sock.send("Login Name?\r\n")
                    return
        users[sock] = []
        users[sock].append(message)
        sock.send("Welcome "+ users[sock][0] +" !\r\n")
    except:
        handleError(sock)
 
#This function is used for chat in rooms
def chat (sock, message):
    if(len(users[sock]) < 2):
        sock.send("Please use /help for command list or /join for joining a chatroom !\r\n")
    else:
        try:
            for key in rooms[users[sock][1]]:
                key.send(users[sock][0]+": " + message +"\r\n")
        except :
            handleError(key)

#This function is used for getting room list
def get_rooms (sock, messagelist):
    try:
        sock.send("Active rooms are:\r\n")
        for key,value in rooms.items():
            sock.send("*" + key +" ("+ str(len(value))+")\r\n")
        sock.send("end of list.\r\n")
    except:
        handleError(sock)

#This function is used for create room and will call join room function afterwards
def create_room (sock, messagelist):
    try:
        if len(users[sock]) > 1:
            sock.send("You need to leave your current room first!\r\n")
        elif len(messagelist) == 1:
            sock.send("You cant create room without name!\r\n")
        elif messagelist[1] in rooms:
            sock.send("Room already exist, Please use /join to join the room\r\n")
        else:
            rooms[messagelist[1]] = [] 
            sock.send("Create room success\r\n")
            join_room(sock,messagelist)
    except:
        handleError(sock)

#This function is used for joining room
def join_room (sock, messagelist):
    if len(messagelist) == 1:
        try:
            sock.send("You cant join room without name!\r\n")
        except:
            handleError(sock)
        return
    roomname = messagelist[1] 
    if roomname in rooms:
        if len(users[sock])>1:
            leave(sock)
        for key in rooms[roomname]:
            try:
                key.send("* new user joined "+ roomname +": " + users[sock][0] +"\r\n")
            except:
                handleError(key)
        try:
            sock.send("entering room: " + roomname +" \r\n")
        except:
            handleError(sock)
        rooms[roomname].append(sock)
        users[sock].append(roomname);
        try:
            for key in rooms[roomname]:
                if key == sock: 
                    sock.send("* " + users[key][0]  +"(** this is you)\r\n")
                else:
                    sock.send(" " + users[key][0] +"\r\n")
            sock.send("end of list\r\n")
        except:
            handleError(sock)
    else:
        try:
            sock.send("Room is not existed. Please create a room or join others room \r\n")
        except:
            handleError(sock)

def leave_room(sock):
    try:
        if(len(users[sock])<2):
            sock.send("You didn't join any room!\r\n")
        else:
            rooms[users[sock][1]].remove(sock)
            sock.send("* user has left chat: "+ users[sock][0]+"(** this is you)\r\n")
            if len(rooms[users[sock][1]]) > 0:
                for key in rooms[users[sock][1]]:
                    key.send("* user has left chat: "+ users[sock][0]+"\r\n")
            else:
                del rooms[users[sock][1]]
            users[sock].pop(1)
    except:
        handleError(sock)

#This function is used for sending private message
def private_chat (sock, messagelist):
    try:
        if len(messagelist) <3:
            sock.send("You cant private chat without name or content!\r\n")
        return
    except:
        handleError(sock)
    for key, value in users.items():
        if len(value) > 0 :
            if messagelist[1] == value[0]:
                try:
                    key.send(users[sock][0]+": "+ " ".join(messagelist[2:])+"\r\n")
                except:
                    handleError(key)
                return
    try:
        sock.send("User not found!\r\n")
    except:
        handleError(key)

#This function is called if user input invalid command
def invalid_command(sock):
    try:
        sock.send("Invalid Commend, Please Try Again\r\n")
    except:
        handleError(sock)

#This function is used for user disconnect
def quit(sock):
    try:
        if(len(users[sock])>1):
            leave_room(sock)
        sock.send("Bye\r\n")
        users.pop(sock,None)
        sock.close()
        CONNECTION_LIST.remove(sock)
    except:
        handleError(sock)

# This function is used to show command list to user
def help(sock):
    try:
        sock.send("/rooms - room list\r\n")
        sock.send("/create roomname- create room\r\n")
        sock.send("/join roomname - join room\r\n")
        sock.send("/leave - leave room\r\n")
        sock.send("/private username message - private message to users\r\n")
        sock.send("/quit - leave chat server\r\n")
    except:
        handleError(sock)

#This function is used for reading input and call approciate function
def command(sock, message): 
    messagelist = message.split()
    if messagelist[0] ==  "/rooms":
        get_rooms(sock,messagelist)
    elif messagelist[0] ==  "/create":
        create_room (sock, messagelist)
    elif messagelist[0] == "/join":
        join_room (sock, messagelist)
    elif messagelist[0] == "/leave":
        leave_room (sock)
    elif messagelist[0] == "/private":
        private_chat (sock, messagelist)
    elif messagelist[0] == "/quit":
        quit(sock)
    elif messagelist[0] == "/help":
        help(sock)
    else:
        invalid_command(sock)

#This function is used for handling error. This will force user disconnect and clear all data of the user
def handleError(sock):
    sock.close()
    if sock in users:
        if len(users[sock]) > 1:
            if users[sock][1] in rooms:
                 rooms[users[sock][1]].remove(sock)
                 if len(rooms[users[sock][1]]) == 0:
                     del rooms[users[sock][1]]
        users.pop(sock,None)
    if sock in CONNECTION_LIST:
        CONNECTION_LIST.remove(sock)


if __name__ == "__main__":
     
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    RECV_BUFFER = 4096
    PORT = 8888
     
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    print "Chat server started on port " + str(PORT)
 
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle new connection
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                try:
                    sockfd.send("Welcome to Chat server\r\n")
                    sockfd.send("Login Name?\r\n")
                except:
                    print "Error 1"
                    handleError(sockfd)
                    continue
            else:
                try:
                    data = sock.recv(RECV_BUFFER)
                    data = data.rstrip("\r\n")
                    if sock in users:
                        if data:
                            if data[0] == "/":
                                command(sock,data)
                            else:
                                chat(sock, data)
                    else:
                        set_name(sock,data)
                except:
                    handleError(sock)
                    continue
    server_socket.close()