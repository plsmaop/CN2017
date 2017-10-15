import socket
import os
import string

BOTName = "NICK ROBOT_tt"
IRCSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def pong(server_msg):
    if server_msg.find("PING") != -1:
        PONG = server_msg.split()[1]
        PONG = "PONG " + PONG +"\r\n"
        print PONG
        IRCSocket.send(PONG)

def read_chan():
    config = open("config", "r")
    config = config.read()
    CHAN =''
    chan_start = False
    for i in config:
        if i == '\'':
            chan_start = not chan_start
            continue
        if chan_start:
            CHAN += i
    #print CHAN 
    return CHAN

def recv_irc():
    server_msg =''
    while True:
        char = IRCSocket.recv(1)
        if char == '\n':
            break
        server_msg += char
    pong(server_msg)
    print (server_msg)
    return server_msg 

def connect(Channel):
    IRCSocket.connect(("irc.freenode.net", 6667))
    IRCSocket.send(BOTName+"\r\n")
    IRCSocket.send("USER ROBOT ROBOT bla :ROBOT\r\n")
    msg_recv = recv_irc()
    IRCSocket.send("JOIN " + Channel + "\r\n")
    IRCSocket.send("PRIVMSG " + Channel+ " :Hello! I am robot.\r\n")

#def convert():
    
    


def reply(Channel, isInChatRoom = False):
    while True:
        msg_recv = recv_irc()
        if msg_recv.find("@ " + Channel) != -1:
            isInChatRoom = True
        if isInChatRoom:
            input_order = raw_input("Please enter something")
            if input_order.find("c") != -1:
                IRCSocket.close()
                print "close the connect"
        
        if msg_recv.find("You have not registered") != -1:
            IRCSocket.close()
            break
        elif msg_recv.find("@repeat ") != -1:
            IRCSocket.send("PRIVMSG " + Channel+ " :havn't finished\r\n")
        elif msg_recv.find("@convert ") != -1:
            IRCSocket.send("PRIVMSG " + Channel+ " :havn't finished\r\n")
        elif msg_recv.find("@ip ") != -1:
            IRCSocket.send("PRIVMSG " + Channel+ " :havn't finished\r\n")
        elif msg_recv.find("@help") != -1:
            IRCSocket.send("PRIVMSG " + Channel+ " :@repeat <Message>\r\n")
            IRCSocket.send("PRIVMSG " + Channel+ " :@convert <Number>\r\n")
            IRCSocket.send("PRIVMSG " + Channel+ " :@ip <String>\r\n")

Channel = read_chan()
connect(Channel)
reply(Channel)


