import argparse
import random

#max wait time in range of randomly choosen waits
random_max = 1000


def insert_line(traffic, time):
    line_num = 0

    for x in range(0,len(traffic)):
        if traffic[x][1] == time:
            line_num = x
            break
    store_line = traffic[line_num]

    del traffic[line_num]
    new_time = time + random.randint(1, random_max)

    found = False
    for x in range(0,len(traffic)):
        if traffic[x][1] > new_time:

            found = True
            break
    if not found:
        traffic.insert(len(traffic), store_line )




"""
    expected arguments: python simulator.py sim_type [gen_file]
"""

parser = argparse.ArgumentParser(description='Get input for Sim Type and Gnerator file')
parser.add_argument("sim_type", help="Type of simulation to run. a - aloha, sa- slotted aloha, c - CSMA 1 persistent")
parser.add_argument("gen_file", nargs='?', help="Filename of file containing generated traffic.", default= "traffic.txt")
args = parser.parse_args()


"""
    Storing the traffic data.
"""
traffic = []
with open(args.gen_file) as f:
    traffic = f.readlines()
traffic = [x.strip() for x in traffic]
# we dont need to know the number of packets
del traffic[0]

ordered_storage = []ordered_storage[count][0]
for line in traffic:
    ordered_storage.append((line, line.split()[-1]),"new")
""" end storage """

""" Implementing ALOHA first """
time_sent = int(traffic[1].split()[-2]) - 1

count = 0
cur_time = 1
"""
while len(ordered_storage) != 0 :
    print "Time: ", cur_time, "Packet ", ordered_storage[count][0].split()[0], ": ", ordered_storage[count][0], "start sending"

    if
    if(ordered_storage[count][-1]+ time_sent < ordered_storage[count + 1][-1] )
"""
