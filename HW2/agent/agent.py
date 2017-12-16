import socket
import sys
#sys.path.append("../mod")
import select
import random
import cPickle as pickle
import os
from struct import *


#Agent_to_Receiver = Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#Agent_to_Sender = Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
Receiver_to_Agent = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
Sender_to_Agent = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SEQNUM = 0
LOSS_RATE = 0
#rebind if the port has already been used
def start():
    while True:
        try:
            print 'Agent: Please ip for listing Sender'
            ip = raw_input()
            print 'Agent: Please enter port for listing Sender'
            port = int(raw_input())
            address = (ip, port)
            Sender_to_Agent.bind(address)
            print address
            return address
            break
        except Exception, e:
            #logger = logging.getLogger('Socket')
            #logger.error('Agent: Failed to bind ' + str(address[1]) + ' : '+ str(e))
            print 'something is wrong'


def send_pkt(pkt, pkt_len_s, receiver_to_agent, rcv_num, drop_num):
    global SEQNUM
    try:
        par_pkt = pickle.loads(pkt)
    except:
        drop_num = drop_num +1
        drop_rate = float(float(drop_num)/float(rcv_num))
        print 'get\tdata\t#' + str(SEQNUM+1)
        print 'drop\tdata\t#' + str(SEQNUM+1) + '\tloss rate =', drop_rate
        return drop_num, True

    pkt_type = par_pkt['Type']
    drop = -1
    if pkt_type == 'data':
        print 'get\t' +  pkt_type + '\t#' + str(par_pkt['SeqNum'])
        random.seed()
        drop = random.randint(1,10000000)
        drop = drop % LOSS_RATE

        if(drop == 0):
            drop_num = drop_num +1
            drop_rate = float(float(drop_num)/float(rcv_num))
            #print drop_rate
            print 'drop\t' + pkt_type + '\t#' + str(par_pkt['SeqNum']) + '\tloss rate =', drop_rate
        else:
            if par_pkt['SeqNum'] == SEQNUM + 1:
                SEQNUM = par_pkt['SeqNum']
            print 'fwd\t' + pkt_type + '\t#' + str(par_pkt['SeqNum']) + '\tloss rate =',  float(float(drop_num)/float(rcv_num))
    elif pkt_type == 'fin':
        print 'get\t' +  pkt_type
        print 'fwd\t' + pkt_type
    if drop != 0:
        Receiver_to_Agent.sendto(pkt_len_s, receiver_to_agent)
        Receiver_to_Agent.sendto(pkt, receiver_to_agent)
    return drop_num, False

def send_ack(ack, ack_len_s, sender_address):
    par_ack = pickle.loads(ack)
    ack_type = par_ack['Type']
    if ack_type == 'ack':
        print 'get\t'+ack_type+ '\t#' + str(par_ack['SeqNum'])
        print 'fwd\t'+ack_type+ '\t#' + str(par_ack['SeqNum'])
    elif ack_type == 'finack':
        print 'get\t'+ack_type
        print 'fwd\t'+ack_type
    Sender_to_Agent.sendto(ack_len_s, sender_address)
    Sender_to_Agent.sendto(ack, sender_address)

def main():
    #select_input = [sys.stdin, Sender_to_Agent, Receiver_to_Agent]
    # initialize
    start()
    print 'Agent: Please ip for fwd pkt to receiver'
    ip = raw_input()
    print 'Agent: Please enter port for fwd pkt to receiver'
    port = int(raw_input())
    receiver_to_agent = (ip, port)
    print 'Agent: Please enter loss rate\nPlease follow the format: \'0.00x\''
    while True:
        try:
            loss_rate = 1/float(raw_input()) 
            break
        except:
            print 'Agent: Please enter loss rate\nPlease follow the format: \'0.00x\''
    global LOSS_RATE
    LOSS_RATE = loss_rate

    exit = False
    drop_num = 0
    rcv_num = 0
    flush = False
    sender_address = ()
    while True:  
        if(exit):
            break
        #for user command
        ready = select.select([sys.stdin, Sender_to_Agent, Receiver_to_Agent],[],[],0.0)[0]
        #command 
        #UDP RECEIVE SOMETHING
        for i in ready:
            if i == Sender_to_Agent:
                rcv_num = rcv_num + 1
                pkt_len_s, sender_address = Sender_to_Agent.recvfrom(4)  
                pkt_len = int(pkt_len_s)
                #print pkt_len
                pkt, sender_address = Sender_to_Agent.recvfrom(pkt_len)
                drop_num, flush = send_pkt(pkt, pkt_len_s, receiver_to_agent, rcv_num, drop_num)
            elif i == Receiver_to_Agent:
                ack_len_s, receiver_address = Receiver_to_Agent.recvfrom(4)
                ack_len = int(ack_len_s)
                ack, address = Receiver_to_Agent.recvfrom(ack_len)
                send_ack(ack, ack_len_s, sender_address)
                    #window = window - 1
            elif i == sys.stdin:
                suck = sys.stdin.readline()
                if(suck == 'suck\n'):
                    print 'Agent: Terminated by User Command'
                    exit = True
    Sender_to_Agent.close()

main()
