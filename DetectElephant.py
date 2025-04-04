#!/usr/bin/python3

#################################################################################################################Imports
from scapy.layers.l2 import Ether #manage L2 Ethernet frames
from scapy.layers.inet import IP, UDP, TCP #manage L3 IPv4 packets, L4 UDP and TCP datagrams
from scapy.packet import Raw #create data payload from crafted packets
from scapy.sendrecv import sniff, sendp #send/capture packets on L2 interfaces
from scapy.utils import wrpcap #save captured packets on .pcap file

import pandas as pd #manipulating data in DataFrame and Series objects
import time #time-related operations

import os #interaction with OS
import argparse #parsing CLI arguments
from filelock import FileLock #ensure thread-safe access to a file
import logging #regulate verbosity of Python runtime output

######################################################################################Elephant Flows Detection Algorithm
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

'''Parse command-line arguments and kickstart on Mininet-emulated servers a process monitoring servers' L2 exit interface (using Scapy sniff() function) to 
   individuate transmitted elephant flows (which surpass a duration threshold and a raw data size threshold)'''
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Monitors traffic between servers (host devices) emulated by Mininet') #argument parser for CLI parameters
    parser.add_argument('--server', type=str, help='Name of this server')
    parser.add_argument('--ipv4', type=str, help='IPv4 address of this server')
    args=parser.parse_args() #parsed arguments

    columns=['detection_count', 'flow_name', 'l4_protocol', 'first_timestamp', 'transmitted_data', 'elephant']
    df=pd.DataFrame(columns=columns) #create dataframe for transmitted flows

    #file_path="./DataFiles/DetectedElephants.csv" #.csv file containing detected elephant flows (enhanced controller)
    #file_path="./DataFiles/DetectedGreedy.csv" #.csv file containing detected elephant flows (enhanced controller + greedy heuristic)
    file_path="./DataFiles/DetectedProb.csv" #.csv file containing detected elephant flows (enhanced controller + probabilistic heuristic)
    lock=FileLock(file_path+".lock") #lock on file to handle concurrent writing by multiple servers

    out_intf=f'{args.server}-eth1' #L2 interface on server
    duration_t=int(100*1024*1024/1450)*0.002 #threshold duration (in seconds) for elephant flows
    size_t=25*1024*1024 #threshold size (in bytes) for elephant flows
    sniff_interval=int(duration_t/2) #time interval for which the algorithm captures packets on L2 exit port
    DSCP_MARK=0b000011<<2 #DS (or TOS equivalently) header field 00001100 (used to mark notification packets for discovered elephant flows)

    detection_count=1 #current iteration of detection algorithm
    duration=30 #duration of detection algorithm
    start_time=time.time() #record of starting instant for detection algorithm

    while time.time()-start_time<duration*60:

        df=df[detection_count-df['detection_count']==1] #filter stale data from dataframe (row not referring to the last iteration)

        #Use BFP filter to capture transmitted packets on server's L2 interface and save them in a PacketList object
        packets_capture=sniff(iface=out_intf, filter=f"ip and src host {args.ipv4} and (tcp or udp)", timeout=sniff_interval, store=1)
        wrpcap(f"./DataFiles/CapturedPackets/{args.server}.pcap",packets_capture) #Optional, save captured packets in a .pcap file

        for packet in packets_capture: #for each Packet object in the PacketList
            if not packet.haslayer(IP): #ignore sniffed packets if L3 protocol is not IPv4
                continue
            elif packet[IP].dst==args.ipv4: #ignore received packets (IPv4 destination is the address of this server)
                continue
            elif packet[IP].src==args.ipv4: #transmitted packets (IPv4 destination is not the address of this server)
                if packet.haslayer(UDP): #process received UDP packets
                    if int(packet[UDP].sport)>int(packet[UDP].dport): #by our convention, L4 destination port should always be greater than L4 source port
                        continue #ignore packet
                    flow_name=f'{packet[IP].src}:{packet[UDP].sport} - {packet[IP].dst}:{packet[UDP].dport}' #obtain flow name from packet's fields
                    protocol="UDP" #flow_name + protocol = 5-tuple
                elif packet.haslayer(TCP): #process received TCP packets
                    if packet[TCP].flags!="P": #ignore all TCP ACK/SYN/SYNACK (do not carry significant load to be distributed)
                        continue
                    if int(packet[TCP].sport)>int(packet[TCP].dport): #by our convention, L4 destination port should always be greater than L4 source port
                        continue #ignore packet
                    flow_name=f'{packet[IP].src}:{packet[TCP].sport} - {packet[IP].dst}:{packet[TCP].dport}' #obtain flow name from packet's fields
                    protocol="TCP" #flow_name + protocol = 5-tuple
                else: #ignore sniffed packets if L4 protocol is neither UDP nor TCP
                    continue

                if flow_name in df['flow_name'].values: #if a row for the transmitted flow already exists in the dataframe
                    flow_row=df.loc[df['flow_name']==flow_name] #fetch existing flow row
                    if detection_count-flow_row['detection_count'].values[0]==1:
                        df.loc[df['flow_name']==flow_name, ['detection_count']]=detection_count #update row detection count in the dataframe
                    if flow_row['elephant'].values[0]: #if the flow has already being marked as elephant
                        continue #ignore packet
                    payload_size=len(packet[Raw].load) if Raw in packet else 0 #get packet payload size
                    data_size=flow_row['transmitted_data'].values[0]+payload_size
                    df.loc[df['flow_name']==flow_name, ['transmitted_data']]=data_size #increment row data size in the dataframe with payload size
                    if packet.time-flow_row['first_timestamp'].values[0]>duration_t: #if duration threshold is triggered
                        if data_size>size_t: #if size threshold is triggered
                            df.loc[df['flow_name']==flow_name, ['elephant']]=True #mark flow as elephant in the dataframe
                            if protocol=='UDP': #create UDP in-band signal packet
                                flag_packet=Ether()/IP(src=packet[IP].src, dst=packet[IP].dst)/UDP(sport=packet[UDP].sport, dport=packet[UDP].dport)
                            else: #create TCP in-band signal packet
                                flag_packet=Ether()/IP(src=packet[IP].src, dst=packet[IP].dst)/TCP(sport=packet[TCP].sport, dport=packet[TCP].dport, flags='P')

                            flag_packet[IP].tos=DSCP_MARK #mark signal packet by setting value of IPv4 DS field (DS field is equivalent to TOS field)
                            sendp(flag_packet, iface=out_intf) #transmit again marked packet on server's L2 exit interface
                            print(f"Elephant flow detected: {flow_name}\n")

                            new_df=pd.DataFrame(df.loc[df['flow_name']==flow_name]) #get updated flow row relative to discovered elephant
                            with lock: #update shared file's content in thread safety
                                file_exists=os.path.isfile(file_path) #checks if the file exists
                                new_df.to_csv(file_path, mode='a', index=False, header=not file_exists) #append to file if it exists, otherwise create a new file

                else: #if there is no row for the received flow in the dataframe
                    new_row=pd.DataFrame([{'detection_count': detection_count,
                                           'flow_name': flow_name,
                                           "l4_protocol": protocol,
                                           'first_timestamp': packet.time, #record instant of transmission of first packet of the flow
                                           'transmitted_data': len(packet[Raw].load) if Raw in packet else 0, #initialize flow size with first payload size
                                           'elephant': False}]) #dictionary initializing a row for the new flow in the dataframe

                    df=pd.concat([df, new_row], ignore_index=True) #add new row to dataframe

            else:
                continue #ignore packet

        detection_count+=1 #increment detection round
        time.sleep(sniff_interval) #wait for a period before starting next iteration