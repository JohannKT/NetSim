import argparse
#max wait time in range of randomly choosen waits
random_max = 1000

class Packet:
    def __init__(self, id, curr_node, send_node, size, time, slotted = False):
        self.id = id
        self.curr_node = curr_node
        self.send_node =send_node
        self.size = size
        if not slotted:
            self.slot_size = 0
            self.time = time
        else:
            self.slot_size = self.size
            self.time = time + (self.slot_size - (time % self.slot_size))
        self.finished_time = self.time + self.size - 1  # the time it takes to send 1 bit is 1 microsecond so it takes size microseconds to send the packet
        self.status = "new"
    def updateTimeSent(self, new_time):
        """
         Used in CSMA to update the time the packet was actually sent after potentially waiting
        :param new_time:
        :return:
        """
        self.time = new_time
        self.finished_time = self.time + self.size - 1
    def dump(self):
        return "Packet {}: {} {} {} {}".format(self.id, self.curr_node, self.send_node, self.size, self.time)
class Wire:
    def __init__(self):
        self.dict = {}
        self.count = 0
        self.state = "idle"
    def add(self, packet):
        if self.dict.has_key(packet.finished_time):
            self.dict[packet.finished_time].append(packet)
        else:
            self.dict[packet.finished_time] = [packet]
        self.state = "busy"
        self.count += 1
    def remove(self, packet):
        if self.dict.has_key(packet.finished_time):
            if packet in self.dict[packet.finished_time]:
                self.dict[packet.finished_time].remove(packet)
                self.count -= 1
                if self.count == 0:
                    self.state = "idle"
                return True
            else:
                return False
        else:
            # print "Packet not on the wire."
            return False
    def clearList(self, index):
        self.count -= len(self.dict[index])
        self.dict[index] = []
        if self.count == 0:
            self.state = "idle"

def chkPrint(msg, ignore=False):
    if not ignore:
        print msg

def aloha(traffic, slotted = False, ignore = False):
    ordered_packets = []
    for line in traffic:
        elements = line.split()
        ordered_packets.append(Packet(int(elements[0]), int(elements[1]), int(elements[2]), int(elements[3]), int(elements[4]), slotted))
    ordered_packets = sorted(ordered_packets, key=lambda p: p.time)  # just in case the generated traffic is not in order
    num_packets = len(ordered_packets)
    successfully_transmitted = 0
    failed = 0
    pkt_size = ordered_packets[0].size # all packet have the same size
    the_wire = Wire() #used to hold packets currently on the wire
    current_time = 0 #time is measured in microseconds but in this context it is equal to one iteration
    #data structure so we don't have to iterate through a list every iteration
    ready_dict = {}
    for p in ordered_packets:
        if ready_dict.has_key(p.time):
            ready_dict[p.time].append(p)
        else:
            ready_dict[p.time] = [p]

    while (successfully_transmitted + failed) < num_packets:
        pkts_ready = ready_dict[current_time] if current_time in ready_dict else []
        pkts_finished = the_wire.dict[current_time] if current_time in the_wire.dict else []

        if len(pkts_ready) > 0:
            # packets are ready to send
            msg_success = "start sending"
            msg_fail = "start sending: collision"
            first_sent = False
            if the_wire.count == 0:
                p = pkts_ready[0]
                chkPrint("Time: {}, {} {}".format(current_time, p.dump(), msg_success), ignore)
                the_wire.add(p)
                first_sent = True
            for i,p in enumerate(pkts_ready):
                if first_sent and i == 0:
                    first_sent = False
                    continue #skip the first packet if it was sent
                p.status = "collision"
                chkPrint("Time: {}, {} {}".format(current_time, p.dump(), msg_fail), ignore)
                the_wire.add(p)

        if len(pkts_finished) > 0:
            msg_success = "finish sending: successfully transmitted"
            msg_fail = "finish sending: failed"
            # packets are finished sending
            if len(pkts_finished) > 1:
                for p in pkts_finished:
                    chkPrint("Time: {}, {} {}".format(current_time, p.dump(), msg_fail), ignore)
                    failed += 1
                the_wire.clearList(current_time)
            elif len(pkts_finished) == 1 and the_wire.count == 1:
                if pkts_finished[0].status == "collision":
                    chkPrint("Time: {}, {} {}".format(current_time, pkts_finished[0].dump(), msg_fail), ignore)
                    failed += 1
                else:
                    chkPrint("Time: {}, {} {}".format(current_time, pkts_finished[0].dump(), msg_success), ignore)
                    successfully_transmitted += 1
                the_wire.remove(pkts_finished[0])
            elif len(pkts_finished) == 1 and the_wire.count > 1:
                for p in pkts_finished:
                    chkPrint("Time: {}, {} {}".format(current_time, p.dump(), msg_fail), ignore)
                    failed += 1
                the_wire.clearList(current_time)
            else:
                # the_wire.count <= 0
                chkPrint("Unexpected Fatal Error: Finished packets that were not on the wire beforehand", ignore)
                exit(0)
        current_time += 1
    chkPrint("{} packets succefully transmitted.".format(successfully_transmitted), ignore)
    chkPrint("{} packets failed transmission due to collision.".format(failed), ignore)
    throughput = (successfully_transmitted*pkt_size)/(float)((current_time-1)*10**-6) #bps
    throughput *= 10**-3 #kbps
    chkPrint("throughput = {}kbps".format(int(throughput)), ignore)
    return (successfully_transmitted, failed, throughput)

def slotted_aloha(traffic, ignore=False):
    return aloha(traffic, True, ignore)

def csma(traffic, ignore=False):
    """
      CSMA without retransmission. We assume the bandwith-delay product is negligible
      1) Check if channel is idle
      2) if idle send packets that are ready to be sent and that are in the wait list, if more than one, collision occurs
      3) else channel is not idle add ready to be sent packets to wait list

    :param traffic: a list of packets as a string (no new line)
    :param ignore: Ignore print statements?
    :return: (successfully_transmitted, failed, throughput)
    """
    num_packets = len(traffic)
    successfully_transmitted = 0
    failed = 0
    the_wire = Wire() #used to hold packets currently on the wire
    current_time = 0 #time is measured in microseconds but in this context it is equal to one iteration
    #data structure so we don't have to iterate through a list every iteration. This saves a lot of time when dealing with a lot of packets
    ready_dict = {}
    elements = [0, 0, 0, 0, 0]
    for l in traffic:
        elements = l.split()
        p = Packet(int(elements[0]), int(elements[1]), int(elements[2]), int(elements[3]), int(elements[4]))
        if ready_dict.has_key(p.time):
            ready_dict[p.time].append(p)
        else:
            ready_dict[p.time] = [p]
    pkt_size = int(elements[3])  # all packet have the same size
    wait_list = [] #this is for csma
    while (successfully_transmitted + failed) < num_packets:
        pkts_ready = ready_dict[current_time] if current_time in ready_dict else []
        pkts_finished = the_wire.dict[current_time] if current_time in the_wire.dict else []

        if len(pkts_ready) == 0 and len(wait_list) > 0 and the_wire.state == "idle":
            #special case the wait_list is not empty and the wire is idle those packets need to be sent
            for p in wait_list:
                pkts_ready.append(p)
            wait_list = []

        if len(pkts_ready) > 0:
            # packets are ready to send
            msg_success = "start sending"
            msg_fail = "start sending: collision"
            if the_wire.state == "idle":
                if len(wait_list) > 0:
                    # if the channel is idle but there are packets on the wait list
                    for p in pkts_ready:
                        wait_list.append(p)
                    first_packet = wait_list[0]
                    first_packet.updateTimeSent(current_time)
                    chkPrint("Time: {}, {} {}".format(current_time, first_packet.dump(), msg_success),ignore)
                    the_wire.add(p)
                    for i, p in enumerate(wait_list):
                        if i != 0:
                            p.updateTimeSent(current_time)
                            p.status = "collision"
                            chkPrint("Time: {}, {} {}".format(current_time, p.dump(), msg_fail),ignore)
                            the_wire.add(p)
                    wait_list = []
                else:
                    p = pkts_ready[0]
                    p.updateTimeSent(current_time)
                    chkPrint("Time: {}, {} {}".format(current_time, p.dump(), msg_success),ignore)
                    the_wire.add(p)
                    for i, p in enumerate(pkts_ready):
                        if i != 0:
                            p.updateTimeSent(current_time)
                            p.status = "collision"
                            chkPrint("Time: {}, {} {}".format(current_time, p.dump(), msg_fail),ignore)
                            the_wire.add(p)
            elif the_wire.state == "busy":
                for p in pkts_ready:
                    wait_list.append(p)
            else:
                print "Error the wire's state is invalid."
                exit(0)

        if len(pkts_finished) > 0:
            msg_success = "finish sending: successfully transmitted"
            msg_fail = "finish sending: failed"
            # packets are finished sending
            if len(pkts_finished) > 1:
                for p in pkts_finished:
                    chkPrint("Time: {}, {} {}".format(current_time, p.dump(), msg_fail),ignore)
                    failed += 1
                the_wire.clearList(current_time)
            elif len(pkts_finished) == 1 and the_wire.count == 1:
                if pkts_finished[0].status == "collision":
                    chkPrint("Time: {}, {} {}".format(current_time, pkts_finished[0].dump(), msg_fail),ignore)
                    failed += 1
                else:
                    chkPrint("Time: {}, {} {}".format(current_time, pkts_finished[0].dump(), msg_success),ignore)
                    successfully_transmitted += 1
                the_wire.remove(pkts_finished[0])
            elif len(pkts_finished) == 1 and the_wire.count > 1:
                for p in pkts_finished:
                    chkPrint("Time: {}, {} {}".format(current_time, p.dump(), msg_fail),ignore)
                    failed += 1
                the_wire.clearList(current_time)
            else:
                # the_wire.count <= 0
                chkPrint("Unexpected Fatal Error: Finished packets that were not on the wire beforehand",ignore)
                exit(0)
        current_time += 1
    chkPrint("{} packets succefully transmitted.".format(successfully_transmitted),ignore)
    chkPrint("{} packets failed transmission due to collision.".format(failed),ignore)
    throughput = (successfully_transmitted*pkt_size)/(float)((current_time-1)*10**-6) #bps
    throughput *= 10**-3 #kbps
    chkPrint("throughput = {}kbps".format(int(throughput)),ignore)
    return (successfully_transmitted, failed, throughput)

def main(gen_file, sim_type):
    try:
        with open(gen_file) as f:
            traffic = f.readlines()
        traffic = [x.strip() for x in traffic]
        del traffic[0]
    except Exception as e:
        print "Failed to read traffic file."
        print "Error {}.".format(e.message)
        return
    if sim_type == 'a':
        aloha(traffic)
    elif sim_type == 'sa':
        slotted_aloha(traffic)
    elif sim_type == 'c':
        csma(traffic)
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
