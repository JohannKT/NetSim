import argparse
import random
import time
import os



""" calculate gap using the following formula:
          pkt_size             offered_load
        --------------    =   ---------------
        pkt_size + gap           num_node
"""

def getKey(item):
    return item[0]

def calculate_gap(args):
    return (((args.pkt_size * args.num_node) / args.offered_load) - args.pkt_size)

def choose_node(args):
    return random.randint(0,args.num_node-1)

def get_send_node(args, cur_node):
    send = random.randint(0,args.num_node-1)
    while send == cur_node:
        send = random.randint(0,args.num_node-1)
    return send

def get_packet_id(args, next_packet, node):
    max_id = args.num_pkts_per_node * args.num_node
    count = 0
    temp = random.randint(0,args.num_node-1 - count)
    while True:
        if(next_packet[node] + args.num_node > max_id):
            return 0
        else:
            next_packet[node] = next_packet[node] + args.num_node
            return 1

def generate_file(args, gap):
    # create dict for keep track of packets sent by each node
    packets_sent = {}
    next_packet = {}
    node_time = {}
    packets_left = args.num_pkts_per_node * args.num_node
    current_time = 0
    output_array= []

    counter = []

    outfile = open("traffic.txt", "w")
    outfile.write(str(packets_left) + "\n")
    #initialize to amount they will each send
    for x in range(0, args.num_node):
        packets_sent[x] = args.num_pkts_per_node
        next_packet[x] = x
        node_time[x] = 0

    #keep going until all values in dict are 0 meaning all have sent their packets
    while  not all(value == 0 for value in packets_sent.values()):
        rand_gap = random.randint(1,2*gap)
        cur_node = 0

        while True:
            cur_node = choose_node(args)
            if packets_sent[cur_node] == 0:
                if all(value == 0 for value in packets_sent.values()):
                    break
                else:
                    cur_node = choose_node(args)
            else:
                break

        send_node = get_send_node(args, cur_node)
        pkt_id = next_packet[cur_node]
        valid = get_packet_id(args, next_packet, cur_node)
        #if not valid:
            #continue
        #update time:
        node_time[cur_node] = node_time[cur_node] + rand_gap
        current_time = node_time[cur_node]
        counter.append(pkt_id)
        temp.remove(pkt_id)
        if not valid:
            if len(output_array) == (args.num_pkts_per_node * args.num_node):
                break



        packets_sent[cur_node] = packets_sent[cur_node] - 1

        output_array.append(  (current_time, str(pkt_id) + " " + str(cur_node) + " " + str(send_node) + " "+ str(args.pkt_size) + " "+ str(current_time) +"\n") )

    output_array = sorted(output_array, key= getKey)

    for x in output_array:
        outfile.write(x[1])


"""handling arguments to the program
expected use is the following:
python generator.py num_node pkt_size offered_load num_pkts_per_node'[seed]
"""
parser = argparse.ArgumentParser(description='Get input to generator')
parser.add_argument("num_node", help="The number of nodes used in simulation.", type=int)
parser.add_argument("pkt_size", help="Size of packets to be  generated.", type=int)
parser.add_argument("offered_load", help=" measure of the traffic compared to the channel capacity.", type=float)
parser.add_argument("num_pkts_per_node", help=" Number of packets sent per node in traffic file generated.", type=int)
parser.add_argument('seed', nargs='?', default=time.time(), type=int)
args = parser.parse_args()


temp = []
for x in range(0, args.num_pkts_per_node * args.num_node):
    temp.append(x)

gap = calculate_gap(args)
generate_file(args, gap)
