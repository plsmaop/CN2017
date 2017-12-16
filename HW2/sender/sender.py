import socket
import sys
import select
import random
import os
import cPickle as pickle
import time
from struct import*
from collections import namedtuple
#sys.path.append("../mod")

DATA_SIZE = 1024
TIME_OUT = 0.1
FILE_PATH = ''
SIZE = 0

def put_zero(zero_num, WINDOW):
    win_len = len(str(WINDOW))
    zero = ''
    while zero_num - win_len > 0:
        zero = zero + '0'
        win_len = win_len + 1
    winSize = zero + str(WINDOW)
    return winSize

def pack(file, cur_size, seqNum):
    global FILE_PATH
    file = file.read(cur_size)
    
    pkt_list = []
    write_data = 0
    while write_data + DATA_SIZE < cur_size:
        pkt = {
            'Type': 'data',
            'SeqNum': seqNum,
            'FileName': FILE_PATH,
            'Data':file[write_data : write_data + DATA_SIZE]
        }
        write_data  = write_data +  DATA_SIZE
        seqNum = seqNum +1
        pkt_list.append(pickle.dumps(pkt, 2))
    pkt = {
        'Type': 'data',
        'SeqNum': seqNum,
        'FileName': FILE_PATH,
        'Data':file[write_data : cur_size]
    }
    pkt_list.append(pickle.dumps(pkt, 2))
    return pkt_list, seqNum + 1
            
def start():
    print 'Sender: Please enter ip'
    ip = raw_input()
    print 'Sender: Please enter port'
    port = int(raw_input())
    print 'Sender: Please enter file path'
    file_path = raw_input()

    while True:
        try:
            file = open(file_path, 'rb')
            break
        except:
            print 'Sender: File open error, please sure the path is right\nPlease re-enter file path:'
            file_path = raw_input()
    global FILE_PATH
    global SIZE
    FILE_PATH = file_path
    SIZE = os.stat(FILE_PATH).st_size
    return (ip, port), file


def main():
    WINDOW = 1
    THRESHOLD = 16
    # initialize
    address, file = start()    
    # prepare for socket
    Sender_to_Agent = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_to_agent = address
    #print sender_to_agent
    select_in = [Sender_to_Agent, sys.stdin]

    
    send_num = 0
    send = True
    exit = False
    resend = False
    oldest_unacked = 1
    resend_base = 0
    rcv_num = 0
    seqNum = 0
    pack_seq_num = 1
    timer = time.time()
    send_count = 0
    cur_pos = 0
    pkt_list = []
    while True:   
        if cur_pos < SIZE:
            readin_size = 0
            if cur_pos + DATA_SIZE * 10240 <= SIZE:
                readin_size = DATA_SIZE * 10240
            else:
                readin_size = SIZE - cur_pos
            pkt_list_tmp, pack_seq_num = pack(file, readin_size, pack_seq_num)
            cur_pos = cur_pos + readin_size
            pkt_list = pkt_list + pkt_list_tmp
            pkt_num = len(pkt_list)
        if exit:
            break
        #fin
        elif seqNum == pkt_num:
            print 'send\tfin'
            fin = {
                'Type' : 'fin'
            }
            fin = pickle.dumps(fin, 2)
            #winSize = '000000000000000' + str(1)
            #Sender_to_Agent.sendto(winSize, sender_to_agent)
            fin_len = len(fin)
            fin_len = put_zero(4, len(fin))
            #print fin_len
            Sender_to_Agent.sendto(fin_len, sender_to_agent) 
            Sender_to_Agent.sendto(fin, sender_to_agent)
            WINDOW = -10000
        #print send_num - oldest_unacked
        if(send_num - oldest_unacked <= WINDOW and send_num < pkt_num):
            pkt = pkt_list[send_num]
            pkt_len = put_zero(4, len(pkt))
            Sender_to_Agent.sendto(pkt_len, sender_to_agent) 
            Sender_to_Agent.sendto(pkt, sender_to_agent) 
                #print pkt_len
            send_num = send_num + 1
                #window = window - 1
            if resend:
                print 'resnd\tdata\t#' + str(send_num) + ',\twinSize = ' + str(WINDOW)
            else:
                print 'send\tdata\t#' + str(send_num) + ',\twinSize = ' + str(WINDOW)
                send_count = send_count + 1
        ready = select.select(select_in, [], [], TIME_OUT)[0]
        for i in ready:
            if i is Sender_to_Agent:
                #timer = time.time()
                ack_len, address = (Sender_to_Agent.recvfrom(4))
                ack, address = Sender_to_Agent.recvfrom(int(ack_len))
                par_ack = pickle.loads(ack)
                ack_type = par_ack['Type']
                if ack_type == 'ack':
                    seqNum = par_ack['SeqNum']
                    print 'recv\t' + ack_type + '\t#' + str(seqNum)
                elif ack_type == 'finack':
                    print 'recv\t' + ack_type 
                    exit = True
                    break
            elif i is sys.stdin:
                in_string = sys.stdin.readline()
                if in_string == 'suck':
                    print 'Sender: User Command: quit'
                    exit = True
        cur_timer = time.time()
        #print cur_timer - timer
        #print 'unakced:', oldest_unacked
        if cur_timer - timer > TIME_OUT and seqNum != oldest_unacked:
            THRESHOLD = max(int(WINDOW/2), 1)
            WINDOW = 1
            print 'time\tout,\t\tthreshold = ' + str(THRESHOLD)
            resend = True
            #send = False
            send_num = oldest_unacked - 1
            rcv_num = 0
            continue
        elif seqNum == oldest_unacked:
            oldest_unacked = oldest_unacked + 1
            timer = time.time()
            rcv_num = rcv_num + 1
            if send_num == send_count:
                resend = False
            if(WINDOW < THRESHOLD):
                WINDOW = WINDOW*2
            else:
                WINDOW = WINDOW+1
            #if rcv_num == send_count:
             #   rcv_num = 0
              #  if resend_base == send_num:
               #     resend = False
                #    send = True
               # elif not resend:
                #    send = True

                #break
        
    file.close()
    Sender_to_Agent.close()
main()