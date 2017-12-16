import socket
import sys
import select
import random
import os
import cPickle as pickle
from struct import*
from collections import namedtuple

BUFFER_SIZE = 32
CUR_SEQ = 0
NAME_EXTENSION = ''
Agent_to_Receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def bind(address):
    while True:
        try:
            print 'Receiver: Please enter ip'
            ip = raw_input()
            print 'Receiver: Please enter port'
            port = int(raw_input())
            address = (ip, port)
            Agent_to_Receiver.bind(address)
            print address
            return address
            break
        except Exception, e:
            print 'Agent: Something is wrong'

def get_name_extension(file_name):
    return '.' + file_name.split('.')[-1]
    
def handle_pkt(pkt, agent_address, BUFFER):
    flush = False
    BUFFER_CUR = len(BUFFER) 
    try:
        par_pkt = pickle.loads(pkt)
    except:
        return False
    pkt_type = par_pkt['Type']
    ack = {}
    global CUR_SEQ
    global NAME_EXTENSION
    #print CUR_SEQ
    if pkt_type == 'data':
        if BUFFER_CUR == 0 and CUR_SEQ + 1  == par_pkt['SeqNum']:
            BUFFER.append(par_pkt)
            print 'recv\t' + pkt_type + '\t#' + str(par_pkt['SeqNum'])
            CUR_SEQ = par_pkt['SeqNum'] 
            if CUR_SEQ == 1:
                NAME_EXTENSION = get_name_extension(par_pkt['FileName'])
            
        elif BUFFER_CUR < BUFFER_SIZE and CUR_SEQ + 1 == par_pkt['SeqNum']:
            BUFFER.append(par_pkt)
            print 'recv\t'+ pkt_type + '\t#' + str(par_pkt['SeqNum'])
            CUR_SEQ = par_pkt['SeqNum'] 
        else:
            flush = True
            print 'drop\t'+ pkt_type + '\t#' + str(par_pkt['SeqNum'])
        print 'send\tack\t#' + str(CUR_SEQ)
        ack = {
            'Type' : 'ack',
            'SeqNum' : CUR_SEQ ,
        }
        #print CUR_SEQ
    elif pkt_type == 'fin':
        print 'recv\t' + pkt_type
        print 'send\tfinack'
        ack = {
            'Type' : 'finack'
        }
    ack = pickle.dumps(ack, 2)
    ack_len = len(ack)
    if ack_len < 10:
        ack_len = '000' + str(ack_len)
    elif ack_len < 100:
        ack_len = '00' + str(ack_len)
    elif ack_len < 1000:
        ack_len = '0' + str(ack_len)
    Agent_to_Receiver.sendto(ack_len, agent_address)
    Agent_to_Receiver.sendto(ack, agent_address)
    if pkt_type == 'fin':
        return True, flush
    else:
        return False, flush
    
def open_file():
    print 'Receiver: Please enter file path'
    file_path = raw_input()
    while True:
        try:
            result = open(file_path + '.tmp', 'a+')
            break
        except:
            print 'Receiver: Open file error\n Please re-enter file path'
            file_path = raw_input() 
    return result, file_path

def main():
    agent_to_receiver = bind(())
    result, file_path = open_file()
    select_in = [Agent_to_Receiver, sys.stdin]
    exit = False
    flush = False
    rcv_count = 0
    BUFFER = []

    while True:
        if (len(BUFFER) == BUFFER_SIZE and flush) or exit:
            for i in BUFFER:
                data = i['Data']
                result.write(data)
            print 'flush'
            BUFFER[:] = []
            flush = False
        if exit:
            break
        ready = select.select(select_in, [], [], 0)[0]
        for i in ready:
            if i == sys.stdin:
                suck = sys.stdin.readline()
                if suck[0:4] == 'suck' or suck == 'suck':
                    print 'Receiver: Terminated by User Command'
                    exit = True
            elif i == Agent_to_Receiver:
                #print 'Receiver: receive selected'
                rcv_count = rcv_count + 1
                pkt_len_s, agent_address = Agent_to_Receiver.recvfrom(4)
                pkt_len = int(pkt_len_s)
                #print pkt_len
                pkt, agent_address = Agent_to_Receiver.recvfrom(pkt_len)
                exit, flush = handle_pkt(pkt, agent_address, BUFFER)
    Agent_to_Receiver.close()
    result.close()
    os.rename(file_path + '.tmp', file_path + NAME_EXTENSION)
main()