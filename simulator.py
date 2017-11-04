import argparse
import random
import IPython
#max wait time in range of randomly choosen waits
random_max = 1000

class Packet:
    def __init__(self, id, curr_node, send_node, size, time):
        self.id = id
        self.curr_node = curr_node
        self.send_node =send_node
        self.size = size
        self.time = time
        self.finished_time = self.time + self.size -1  #the time it takes to send 1 bit is 1 microsecond so it takes size microseconds to send the packet
        self.status = "new"
    def dump(self):
        return "Packet {}: {} {} {} {}".format(self.id, self.curr_node, self.send_node, self.size, self.time)

class Wire:
    def __init__(self):
        self.dict = {}
        self.count = 0
    def add(self, packet):
        if self.dict.has_key(packet.finished_time):
            self.dict[packet.finished_time].append(packet)
        else:
            self.dict[packet.finished_time] = [packet]
        self.count += 1
    def remove(self, packet):
        if self.dict.has_key(packet.finished_time):
            if packet in self.dict[packet.finished_time]:
                self.dict[packet.finished_time].remove(packet)
                self.count -= 1
                return True
            else:
                return False
        else:
            # print "Packet not on the wire."
            return False
    def clearList(self, index):
        self.count -= len(self.dict[index])
        self.dict[index] = []


def aloha2(ordered_packets):
    successfully_transmitted = 0
    failed = 0
    throughput = 0
    pkt_size = ordered_packets[0].size # all packet have the same size
    the_wire = Wire() #used to hold packets currently on the wire
    current_time = 0 #time is measured in microseconds but in this context it is equal to one iteration
    max_time = max(ordered_packets, key= lambda p : p.finished_time).finished_time
    #data structure so we don't have to iterate through a list every iteration
    ready_dict = {}
    for p in ordered_packets:
        if ready_dict.has_key(p.time):
            ready_dict[p.time].append(p)
        else:
            ready_dict[p.time] = [p]

    for i in range(0, max_time+1):
        pkts_ready = ready_dict[current_time] if current_time in ready_dict else []
        pkts_finished = the_wire.dict[current_time] if current_time in the_wire.dict else []

        if len(pkts_ready) > 0:
            # packets are ready to send
            msg_success = "start sending"
            msg_fail = "start sending: collision"
            first_sent = False
            if the_wire.count == 0:
                p = pkts_ready[0]
                print "Time: {}, {} {}".format(current_time, p.dump(), msg_success)
                the_wire.add(p)
                first_sent = True
            for i,p in enumerate(pkts_ready):
                if first_sent and i == 0:
                    first_sent = False
                    continue #skip the first packet if it was sent
                p.status = "collision"
                print "Time: {}, {} {}".format(current_time, p.dump(), msg_fail)
                the_wire.add(p)

        if len(pkts_finished) > 0:
            msg_success = "finish sending: successfully transmitted"
            msg_fail = "finish sending: failed"
            # packets are finished sending
            if len(pkts_finished) > 1:
                for p in pkts_finished:
                    print "Time: {}, {} {}".format(current_time, p.dump(), msg_fail)
                    failed += 1
                the_wire.clearList(current_time)
            elif len(pkts_finished) == 1 and the_wire.count == 1:
                if pkts_finished[0].status == "collision":
                    print "Time: {}, {} {}".format(current_time, pkts_finished[0].dump(), msg_fail)
                    failed += 1
                else:
                    print "Time: {}, {} {}".format(current_time, pkts_finished[0].dump(), msg_success)
                    successfully_transmitted += 1
                the_wire.remove(pkts_finished[0])
            elif len(pkts_finished) == 1 and the_wire.count > 1:
                for p in pkts_finished:
                    print "Time: {}, {} {}".format(current_time, p.dump(), msg_fail)
                    failed += 1
                the_wire.clearList(current_time)
            else:
                # the_wire.count <= 0
                print "Unexpected Fatal Error: Finished packets that were not on the wire beforehand"
                exit(0)
        current_time += 1
    print "{} packets succefully transmitted.".format(successfully_transmitted)
    print "{} packets failed transmission due to collision.".format(failed)
    throughput = (successfully_transmitted*pkt_size)/(float)((current_time-1)*10**-6) #bps
    throughput *= 10**-3 #kbps
    print "throughput = {}kbps".format(int(throughput))


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

def aloha1(traffic, ordered_storage):
    # this is the packet size / 1e6 bps = 1*packet_size microsecond A.K.A just the packet size
    time_sent = int(traffic[1].split()[-2]) - 1 #time it takes to send the packet

    curr_wire = []
    count = 0
    cur_time = 0 #each iteration equals 1 "micro second"
    """ temp has list of (ordered storage, position in ordered storage) """
    """ cur_wire has list of (time finished, "success or failed", position in ordered_storage) """
    while count != len(ordered_storage):
        if len(curr_wire) > 0:
            deletion_list = []
            for x in range(0, len(curr_wire)):
                if curr_wire[x][0] == cur_time:
                    if curr_wire[x][1] == "success":
                        print "Time: ", cur_time, "Packet ", ordered_storage[curr_wire[x][2]][0].split()[0], ": ", \
                        ordered_storage[curr_wire[x][2]][0], " finish sending: successfully transmitted"
                        deletion_list.append(curr_wire[x])
                        # del ordered_storage[curr_wire[x][2]]
                        # del curr_wire[x]

                    else:
                        print "Time: ", cur_time, "Packet ", ordered_storage[curr_wire[x][2]][0].split()[0], ": ", \
                        ordered_storage[curr_wire[x][2]][0], " finish sending: failed"
                        deletion_list.append(curr_wire[x])
                        # del ordered_storage[curr_wire[x][2]]
                        # del curr_wire[x]
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
                    curr_wire.append((temp[x][0] + time_sent - 1, "success", temp[x][1]))
                    print "Time: ", cur_time, "Packet ", ordered_storage[temp[x][1]][0].split()[0], ": ", \
                    ordered_storage[temp[x][1]][0], "start sending"
                else:
                    #this will never occur because curr_wire always has elements at this point
                    curr_wire.append((temp[x][0] + time_sent, "collision", temp[x][1]))
                    print "Time: ", cur_time, "Packet ", ordered_storage[temp[x][1]][0].split()[0], ": ", \
                    ordered_storage[temp[x][1]][0], "start sending: collision"
            elif len(temp) == 1 and len(curr_wire) == 0:
                curr_wire.append((temp[x][0] + time_sent, "success", temp[x][1]))
                print "Time: ", cur_time, "Packet ", ordered_storage[temp[x][1]][0].split()[0], ": ", \
                ordered_storage[temp[x][1]][0], "start sending"
            else:
                curr_wire.append((temp[x][0] + time_sent, "collision", temp[x][1]))
                print "Time: ", cur_time, "Packet ", ordered_storage[temp[x][1]][0].split()[0], ": ", \
                ordered_storage[temp[x][1]][0], "start sending: collision"
        cur_time = cur_time + 1
        # print "the current length of ordered_storage: ", len(ordered_storage)
        # print "the current length of wire: ", len(curr_wire)

def main(gen_file, sim_type):
    #read traffic
    traffic = []
    try:
        with open(args.gen_file) as f:
            traffic = f.readlines()
        traffic = [x.strip() for x in traffic]
        del traffic[0]
    except Exception as e:
        print "Failed to read traffic file."
        print "Error {}.".format(e.message)
        return
    ordered_storage = []
    ordered_packets = []
    for line in traffic:
        ordered_storage.append((line, int(line.split()[-1]), "new"))
        elements = line.split()
        ordered_packets.append(Packet(int(elements[0]), int(elements[1]), int(elements[2]), int(elements[3]), int(elements[4])))
    ordered_storage = sorted(ordered_storage, key=lambda b: b[1])  # just in case the generated traffic is not in order
    ordered_packets = sorted(ordered_packets, key=lambda p: p.time)  # just in case the generated traffic is not in order
    if sim_type == 'a':
        #aloha1(traffic, ordered_storage)
        aloha2(ordered_packets)
    else:
        print "Simulation type {} is not implemented".format(sim_type)
        print "Options are: 'a' - aloha, 'sa'- slotted aloha, 'c' - CSMA 1 persistent"
    pass


if __name__ == "__main__":
    """
        expected arguments: python simulator.py sim_type [gen_file]
    """

    parser = argparse.ArgumentParser(description='Get input for Sim Type and Gnerator file')
    parser.add_argument("sim_type", help="Type of simulation to run. a - aloha, sa- slotted aloha, c - CSMA 1 persistent")
    parser.add_argument("gen_file", nargs='?', help="Filename of file containing generated traffic.", default= "traffic.txt")
    args = parser.parse_args()
    main(args.gen_file, args.sim_type)




