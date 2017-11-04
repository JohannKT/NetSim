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

def calculate_gap(pkt_size, num_node, offered_load):
    #TODO right now we force it to be an int but we need to figure out if it is the floor or ceiling we should be using
    return int((((pkt_size * num_node) / offered_load) - pkt_size))

def choose_node(num_node):
    return random.randint(0,num_node-1)

def get_send_node(num_node, cur_node):
    send = random.randint(0,num_node-1)
    while send == cur_node:
        send = random.randint(0,num_node-1)
    return send

def get_packet_id(num_pkts_per_node, num_node, next_packet, node):
    '''
      Packet IDs are determined by using the next_packet dictionary. This dictionary original containes the node number + 1.
      Each node determines it's next packet id by adding the number of nodes to it's current packet ID.
      Ex. Node 1's first packet ID will be 2. It's next ID will be 2+num_nodes and it's next ID will be 2+2*num_nodes and so on.
    '''
    max_id = num_pkts_per_node * num_node
    if(next_packet[node] + num_node > max_id):
        return 0 #failed
    else:
        next_packet[node] = next_packet[node] + num_node
        return 1 #success
    
def generate_file(num_node, pkt_size, offered_load, num_pkts_per_node, seed, gen_file = True):
    # create dict for keeping track of packets sent by each node
    # Each dict's key is the node number
    gap = calculate_gap(pkt_size, num_node, offered_load)
    packets_sent = {} 
    next_packet = {} 
    node_time = {}
    packets_left = num_pkts_per_node * num_node #total number of packets
    current_time = 0
    output_array= []

    counter = []

    if gen_file:
        outfile = open("traffic.txt", "w")
        outfile.write(str(packets_left) + "\n") #per project guidlines, the first line of output should be the total number of packets in the file
    #initialize to amount they will each send
    for x in range(0, num_node):
        packets_sent[x] = num_pkts_per_node
        next_packet[x] = x
        node_time[x] = 0

    #keep going until all values in dict are 0 meaning all have sent their packets
    while  not all(value == 0 for value in packets_sent.values()):
        rand_gap = random.randint(1,2*gap)
        cur_node = 0

        while True:
            cur_node = choose_node(num_node)
            if packets_sent[cur_node] == 0:
                if all(value == 0 for value in packets_sent.values()):
                    break
                else:
                    cur_node = choose_node(num_node)
            else:
                break

        send_node = get_send_node(num_node, cur_node)
        pkt_id = next_packet[cur_node]
        valid = get_packet_id(num_pkts_per_node, num_node, next_packet, cur_node)
        #if not valid:
            #continue
        #update time:
        node_time[cur_node] = node_time[cur_node] + rand_gap
        current_time = node_time[cur_node]
        counter.append(pkt_id)
        if not valid:
            if len(output_array) == (num_pkts_per_node * num_node):
                break

        packets_sent[cur_node] = packets_sent[cur_node] - 1

        output_array.append(  (current_time, str(pkt_id) + " " + str(cur_node) + " " + str(send_node) + " "+ str(pkt_size) + " "+ str(current_time) +"\n") )

    output_array = sorted(output_array, key= getKey)
    if gen_file:
        for x in output_array:
            outfile.write(x[1])
    return [x[1] for x in output_array]


if __name__ == "__main__":
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
    #this is just so it easier to call generate_file from a script (so we can auto generate traffic)
    generate_file(args.num_node, args.pkt_size, args.offered_load, args.num_pkts_per_node, args.seed)
