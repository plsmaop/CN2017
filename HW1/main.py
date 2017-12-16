import socket

BOTName = "DEss232"
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
    IRCSocket.send("NICK " + BOTName + "\r\n")
    IRCSocket.send("USER ROBOT ROBOT bla :ROBOT\r\n")
    msg_recv = recv_irc()
    IRCSocket.send("JOIN " + Channel + "\r\n")
    IRCSocket.send("PRIVMSG " + Channel+ " :Hello! I am robot.\r\n")

#def reapt_all(msg_recv, repeat_start_pos):
    

def repeat(msg_recv):
    #print msg_recv
    repeat_pos = msg_recv.find("@repeat ") + 8
    return msg_recv[repeat_pos:]
    #return msg_recv[repeat_pos:len(msg_recv) - 1]
    
def convert(msg_recv):
    convert_number  = msg_recv[msg_recv.find("@convert ") + 9:]
    try:
        return str(hex(int(convert_number)))
    except ValueError:
        try:
            return str(int(convert_number, 16))
        except ValueError:
            return "Input_Error"

def isValid(ip_string):
    length = len(ip_string)
    if length == 0 or length > 3 or (length > 1 and ip_string[0] == '0'):
        return False
    try:
        ip_number = int(ip_string)
    except:
        print ip_string
        return False
    return ip_number >= 0 and ip_number <= 255

def ip_caculator(ip_string, segment_number, valid_ip, ip_list):
    if segment_number == 0 and len(ip_string) == 0: ip_list.append(valid_ip)
    else:
        for i in range(1,4):
            if len(ip_string) >= i and isValid(ip_string[:i]):
                if segment_number == 1: ip_caculator(ip_string[i:], segment_number - 1, valid_ip + ip_string[:i], ip_list)
                else: ip_caculator(ip_string[i:], segment_number - 1, valid_ip + ip_string[:i] + '.', ip_list)

def ip(msg_recv):
    ip_start_pos = msg_recv.find("@ip ") + 4
    ip_string =  msg_recv[ip_start_pos:]
    print ip_string
    if len(ip_string) < 4 or len(ip_string) > 12:
        return
    ip_list = []
    ip_caculator(ip_string, 4, '', ip_list)
    return ip_list

def reply(Channel, isInChatRoom = False):
    while True:
        msg_recv = recv_irc()
        if msg_recv.find("@ " + Channel) != -1:
            isInChatRoom = True
        
        if msg_recv.find("You have not registered") != -1:
            IRCSocket.close()
            break
        elif msg_recv.find("@repeat ") != -1:
            IRCSocket.send("PRIVMSG " + Channel+ " :" + repeat(msg_recv) +"\r\n")
        elif msg_recv.find("@convert ") != -1:
            IRCSocket.send("PRIVMSG " + Channel+ " :" + convert(msg_recv) + "\r\n")
        elif msg_recv.find("@ip ") != -1:
            ip_list = ip(msg_recv)
            ip_len = ''
            try:
                ip_len = str(len(ip_list))
            except:
                ip_len = '0'
            IRCSocket.send("PRIVMSG " + Channel+ " :" + ip_len + "\r\n")
            if not ip_len == '0':
                for i in ip_list:
                    IRCSocket.send("PRIVMSG " + Channel+ " :" + i + "\r\n")
        elif msg_recv.find("@help") != -1:
            IRCSocket.send("PRIVMSG " + Channel+ " :@repeat <Message>\r\n")
            IRCSocket.send("PRIVMSG " + Channel+ " :@convert <Number>\r\n")
            IRCSocket.send("PRIVMSG " + Channel+ " :@ip <String>\r\n")

Channel = read_chan()
connect(Channel)
reply(Channel)
