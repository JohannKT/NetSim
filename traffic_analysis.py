import generator
import simulator
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime
from multiprocessing.pool import ThreadPool


def getTraffic(num_node, pkt_size, offered_load, num_pkts_per_node, seed = time.time()):
    """
    Generates traffic based on the parameters and returns it in a way that it can be passed to the simlator functions
    :return:
    """
    generate_file = False #for readability
    traffic = generator.generate_file(num_node, pkt_size, offered_load, num_pkts_per_node, seed, generate_file)
    del traffic[0]
    traffic = [x.strip() for x in traffic]
    return traffic

def alohaAnalysis(traffic):
    """

    :param traffic: should be the return value of getTraffic
    :return: returns a tuple (successfully_transmitted, failed, throughput)
    """
    ignore_output = True
    slotted = False
    return simulator.aloha(traffic, slotted, ignore_output)


def slottedAlohaAnalysis(traffic):
    """

    :param traffic: should be the return value of getTraffic
    :return: returns a tuple (successfully_transmitted, failed, throughput)
    """
    return simulator.slotted_aloha(traffic, True)


def csmaAnalysis(traffic):
    """

    :param traffic: should be the return value of getTraffic
    :return: returns a tuple (successfully_transmitted, failed, throughput)
    """
    return simulator.csma(traffic, True)

def generateGraph(vals):
    """
      Plot the graph similar to Figure 4-4 on page 268 of the text book
    :param vals: Dictionary containing Aloha:[(utilization,offered_load),..], Slotted:[(utilization,offered_load),..], CSMA:[(utilization,offered_load),..]
    :return: None
    """
    #TODO convert throughput to utilization
    for key,v in vals.items():
        if key == "Aloha":
            type = 'b-' #blue
        elif key == "Slotted_Aloha":
            type = 'g-' #green
        elif key == "CSMA":
            type = 'r-' #red
        else:
            type = 'y-' #shouldn't be possible
        x_vals = [y[1] for y in v]
        y_vals = [y[0] for y in v]
        plt.plot(x_vals, y_vals, type, label=key)

    plt.xlabel("G (attempts per packet time)")
    plt.xticks(np.arange(0, 8.5 + 0.5, 0.5))
    plt.ylabel("S (throughput per packet time)")
    plt.legend(loc='best')
    plt.savefig("{}_range_{}_{}.png".format(str(datetime.datetime.today()).replace(' ', '_'), 0.5, 8.5))
    plt.show() # should probably create png or something

def main():
    throughput_to_offeredLoad = {"Aloha":[], "Slotted_Aloha":[], "CSMA":[]}
    offered_loads = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0]
    num_node = 10
    pkt_size = 100
    num_pkts_per_node = 10000 # total of 100,000 packets per requirements
    max_utilization = 1000.0 #1000 kbps = 1mbps, we are at max if we are using the entire 1mbps
    pool = ThreadPool(processes=3)

    for ol in offered_loads:
        print "Trying load: {}".format(ol)
        traffic = getTraffic(num_node, pkt_size, ol, num_pkts_per_node)
        #returns (successfully_transmitted, failed, throughput(in kbps))
        aloha = pool.apply_async(alohaAnalysis, ([traffic]))
        s_aloha = pool.apply_async(slottedAlohaAnalysis, ([traffic]))
        csma = pool.apply_async(csmaAnalysis, ([traffic]))
        throughput_to_offeredLoad["Aloha"].append((aloha.get()[2] / max_utilization, ol))
        throughput_to_offeredLoad["Slotted_Aloha"].append((s_aloha.get()[2] / max_utilization, ol))
        throughput_to_offeredLoad["CSMA"].append((csma.get()[2]/max_utilization, ol))
        if ol == 1.5:
            break # DEBUG just do it once for now
    generateGraph(throughput_to_offeredLoad)

if __name__ == "__main__":
    main()