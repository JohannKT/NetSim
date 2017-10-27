import argparse
import random
import time
import os



""" calculate gap using the following formula:
          pkt_size             offered_load
        --------------    =   ---------------
        pkt_size + gap           num_node
"""

def calculate_gap(args):
    return ((args.pkt_size * args.num_node) / args.offered_load) - args.pkt_size



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
