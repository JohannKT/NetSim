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

ordered_storage =[]
for line in traffic:
    ordered_storage.append((line, int(line.split()[-1] ),"new"))
""" end storage """

""" Implementing ALOHA first """
time_sent = int(traffic[1].split()[-2]) - 1
curr_wire = []
count = 0
cur_time = 0


""" temp has list of (ordered storage, position in ordered storage) """
""" cur_wire has list of (time finished, "success or failed", position in ordered_storage) """
while count != len(ordered_storage):

    if len(curr_wire) > 0:
        deletion_list = []
        for x in range(0, len(curr_wire)):
            if curr_wire[x][0] == cur_time:
                if curr_wire[x][1] == "success":
                    print "Time: ", cur_time, "Packet ", ordered_storage[curr_wire[x][2]][0].split()[0], ": ", ordered_storage[curr_wire[x][2]][0], " finish sending: successfully transmitted"
                    deletion_list.append( curr_wire[x] )
                    #del ordered_storage[curr_wire[x][2]]
                    #del curr_wire[x]

                else:
                    print "Time: ", cur_time, "Packet ", ordered_storage[curr_wire[x][2]][0].split()[0], ": ", ordered_storage[curr_wire[x][2]][0], " finish sending: failed"
                    deletion_list.append( curr_wire[x] )
                    #del ordered_storage[curr_wire[x][2]]
                    #del curr_wire[x]
        for x in deletion_list:
            count = count + 1
            curr_wire.remove(x)


    temp = []
    for x in range(0, len(ordered_storage)):
        if ordered_storage[x][1] == cur_time:
            temp.append((cur_time, x))
    """
    if temp > 0 and len(curr_wire) > 0:
        for x in range(0, len(curr_wire)):
            curr_wire[x] = (curr_wire[x][0], "failed", curr_wire[x][2])
    """        
    for x in range(0, len(temp)):
        if len(temp) > 1 and len(curr_wire) == 0:
            if x == 0:
                curr_wire.append( (temp[x][0] + time_sent-1, "success", temp[x][1]) )
                print "Time: ", cur_time, "Packet ", ordered_storage[temp[x][1]][0].split()[0], ": ", ordered_storage[temp[x][1]][0], "start sending"
            else:
                curr_wire.append( (temp[x][0] + time_sent, "collision", temp[x][1]) )
                print "Time: ", cur_time, "Packet ", ordered_storage[temp[x][1]][0].split()[0], ": ", ordered_storage[temp[x][1]][0], "start sending: collision"
        elif len(temp) == 1 and len(curr_wire) == 0:
            curr_wire.append( (temp[x][0]+ time_sent, "success", temp[x][1]) )
            print "Time: ", cur_time, "Packet ", ordered_storage[temp[x][1]][0].split()[0], ": ", ordered_storage[temp[x][1]][0], "start sending"
        else:
            curr_wire.append( (temp[x][0] + time_sent, "collision", temp[x][1]) )
            print "Time: ", cur_time, "Packet ", ordered_storage[temp[x][1]][0].split()[0], ": ", ordered_storage[temp[x][1]][0], "start sending: collision"
    cur_time = cur_time + 1
    #print "the current length of ordered_storage: ", len(ordered_storage)
    #print "the current length of wire: ", len(curr_wire)
