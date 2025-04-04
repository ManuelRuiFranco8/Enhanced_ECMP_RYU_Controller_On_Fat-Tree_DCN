#!/usr/bin/env python3

"""This script uses Ryu library to define a centralized SDN controller for our DCN. We implement default proactive static ECMP routing for unicast
flows, fat-tree specific proactive broadcast routing, and dynamic reactive routing for elephant flows
Running command:
ryu-manager RyuEnhancedECMPController.py"""

#################################################################################################################Imports
from ryu.base import app_manager #base class for Ryu controller
from ryu.ofproto import ofproto_v1_3 #handle OpenFlow 1.3 protocol
from ryu.ofproto.ofproto_v1_3 import OFPP_ANY #request stats for all ports of an emulated switch
from ryu.controller import ofp_event #contain following OF events: SwitchFeatures, PacketIN, PortStatsReply
from ryu.controller.dpset import EventDP #event to handle connection/disconnection of switches
from ryu.topology.event import EventLinkAdd, EventLinkDelete, EventHostAdd #events to handle presence/absence of links/servers
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER #operational states in switch-controller connection
from ryu.controller.handler import set_ev_cls #decorator for event-handler methods
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, arp, tcp, udp #utilities for packet managing
from ryu.ofproto import inet #utilities for IP protocol
from ryu.app.wsgi import WSGIApplication, ControllerBase, Response, route #framework to define REST API endpoint

from fatTreeTopo import FatTree #custom class defining the topology deployed by Mininet
import networkx as nx #framework providing functions on graph objects

import threading #instantiate and running threads (performing operations in parallel)
import subprocess #running shell commands
import os #interaction with OS

import time #time-related operations
from datetime import datetime as dt #date-related operations
import pandas as pd #manipulating data in DataFrame and Series objects
import math #mathematical functions
import ast #analysing data with an "Abstract Syntax Tree"
import json #functions to work with JSON format
import hashlib #secure hashing functions

########################################################################################################Global Variables
conf_path="./controllerConf.txt" #file containing custom configuration info for Ryu controller (relating topology object deployed by Mininet)
log_path="./LogFiles/enhancedControllerLog.txt" #file where controller saves logs of all performed operations
stat_folder="./DataFiles" #path where controller saves statistical data about OVS switches port stats

REST_API_INSTANCE_NAME='rest_api_controller' #Name of WSGI web server instance
url='http://localhost:8080/congestiondata' #REST API endpoint

##################################################################################################Controller Application
class ECMP13(app_manager.RyuApp): #extends base class app_manager.RyuApp

    ####################################################################################################Class attributes
    OFP_VERSIONS=[ofproto_v1_3.OFP_VERSION] #set OpenFlow protocol version (1.3)

    __MONITORING_INTERVAL=60 #starting monitoring interval for querying port stats from OVS switches
    __BASE_INTERVAL=20 #used to dynamically change the monitoring interval
    __MIN_INTERVAL=40 #minimum monitoring interval
    __MAX_INTERVAL=80 #maximum monitoring interval
    __QUERY_COUNT=1 #how many times ports stats have been queried

    _CONTEXTS={'wsgi': WSGIApplication}

    #################################################################################Constructor and instance attributes
    '''Creates instance of ECMP13 controller application, initialize instance attributes
       @param *args positional arguments (passed by Ryu.app_manager)
       @param **kwargs keywords arguments (passed by Ryu.app_manager)'''
    def __init__(self, *args, **kwargs):
        with open(log_path, "w") as log_file:
            log_file.write(f"{dt.now()} -> Initialize controller\n")
        super(ECMP13, self).__init__(*args, **kwargs) #constructor of superclass RyuApp

        wsgi=kwargs['wsgi']
        wsgi.register(RestController, {REST_API_INSTANCE_NAME: self}) #register ECMP13 instance to web server instance

        try:
            with open(conf_path, 'r') as file: #it reads the configuration file and assign values to controller instance's attributes
                for line in file:
                    param, value=line.strip().split(": ") #it splits the line into a <key, value> pair
                    if param=="k":
                        self.__k=int(value) #it converts read value to integer
                        print("Number of ports per switch: ", self.__k)
                    elif param=="link_bw":
                        self.__bw=ast.literal_eval(value) #bandwidth [Mbps] for topology links
                        print("Links bandwidth: ", self.__bw)
                    elif param=="link_loss":
                        self.__loss=ast.literal_eval(value) #loss percentage for topology links
                        print("Loss percentage on links: ", self.__loss)
                    elif param=="link_delay":
                        self.__delay=ast.literal_eval(value) #delay [ms] for topology links
                        print("Average delay on links: ", self.__delay)
                    elif param=="link_jitter":
                        self.__jitter=ast.literal_eval(value) #jitter [ms] for topology links
                        print("Average jitter on links: ", self.__jitter)
                    elif param=="link_max_queue":
                        self.__max_queue=ast.literal_eval(value) #maximum port queue size for topology links
                        print("Maximum queue size on switch's ports: ", self.__max_queue)
                    elif param=="arp": #value=="True" if static arp is enabled in the DCN (servers' ARP tables are computed statically)
                        self.__static_arp=(value=="True") #it converts read value to boolean
                    else:
                        raise ValueError(f'Incorrect network configurations in file {conf_path}.')
        except FileNotFoundError:
            print(f"Error: The file '{conf_path}' does not exist.")
        except ValueError:
            print(f'Incorrect network configurations in file {conf_path}.')

        #reference to a topology object equivalent (same nodes and links) to the one deployed by Mininet
        self.__topo=FatTree(k=self.__k, bw=self.__bw, loss=self.__loss, delay=self.__delay, jitter=self.__jitter, max_queue=self.__max_queue)

        self.graph=nx.Graph() #Graph object representing an overlay undirected graph of the network (handles switch/server connections and link failures)

        with open(log_path, "a") as log_file:
            log_file.write(f"{dt.now()} -> Created overlay graph of type: {'Directed' if self.graph.is_directed() else 'Undirected'}\n")
            log_file.write(f"{dt.now()} -> Static server's ARP tables: {'Yes' if self.__static_arp else 'No'}\n")

        self.__datapaths={} #dictionary of datapath objects in the topology (references to OVS switches connected to controller) <int DPID: datapath>
        self.__servers={} #dictionary of host objects (references to servers in the topology) <str MAC: host>
        self.__firstConnection=True #flag: True if network is booting for first time

        self.__broadcastAddress=self.__topo.broadcast_address #network's broadcast address

        self.__link_df=pd.DataFrame() #DataFrame object containing current link statistics

        self.__broadcast_rules={} #dictionary recording the group rules installed in each switch to route broadcast flows
        self.__elephant_rules={} #dictionary recording the group rules installed in each switch to route elephant flows

        #file_path=os.path.join(stat_folder, "LinkStatsEnhanced.csv") #(enhanced controller)
        #file_path=os.path.join(stat_folder, "LinkStatsGreedy.csv") #(enhanced controller + greedy heuristic)
        file_path=os.path.join(stat_folder, "LinkStatsProb.csv") #(enhanced controller + probabilistic heuristic)
        if os.path.isfile(file_path):
            os.remove(file_path) #clear file where topology link's stats are recorder every time the controller is started

        with open(log_path, "a") as log_file:
            log_file.write(f"{dt.now()} -> Data center broadcast address: {self.__broadcastAddress}\n")
            log_file.write(f"{dt.now()} -> Controller initialized\n")
            log_file.write(f"\n")

        try: #starting threads
            t1=threading.Thread(target=self.request_stats, args=()) #thread periodically querying port stats on connected OVS kernel switches
            t1.start()
            t2=threading.Thread(target=self.recompute_paths, args=()) #thread periodically refreshing default static ECMP flow rules and broadcast rules
            t2.start()
        except Exception as e:
            print(e)

    ################################################################################################### Thread Functions
    '''Thread function periodically (with a dynamically adjusted period) requesting port stats to connected OVS switches
       @param ECMP13 object'''
    def request_stats(self):
        while self.__firstConnection: #thread waits until network boot-up is completed (__firstConnection==False)
            time.sleep(5) #check value of flag __firstConnection every 5 seconds
        while not self.__firstConnection: #after network boot-up, periodically request port stats on active OVS switches
            if len(self.graph.nodes)==0: #if the overlay graph is empty, the network has been shut down, so thread needs to terminate
                with open(log_path, "a") as log_file:
                    log_file.write(f'{dt.now()} -> Network has shut down, request stat thread terminates\n')
                return

            try:
                if len(self.__link_df)>0: #clear link stat dataframe from outdated info (related to links that have fallen/have been disconnected)
                    self.__link_df.drop(self.__link_df[self.__QUERY_COUNT-self.__link_df['query_count']!=1].index, inplace=True)
            except IndexError:
                print('IndexError: trying to drop an empty row set from the dataframe')
            except KeyError:
                print("KeyError: 'query-count' is not a valid key in the dataframe")
            except TypeError:
                print('TypeError: fields are none or contains non-numeric data')

            print(f"Query count: {self.__QUERY_COUNT}")
            print(f'Monitoring interval: {self.__MONITORING_INTERVAL}')
            for dpid in self.__datapaths.keys(): #for each OVS switch registered on the controller
                try:
                   datapath=self.__datapaths[dpid] #reference to current OVS switch. If the switch is currently not connected, this is None
                   parser=datapath.ofproto_parser #to create manage OF messages

                   req_port=parser.OFPPortStatsRequest(datapath=datapath, port_no=OFPP_ANY) #create OF message requesting port stats for all switch's ports
                   datapath.send_msg(req_port) #controller sends request to current OVS switch

                   switch_name=self.__topo.get_name(dpid=dpid)
                   print(f"sent request to switch {switch_name}")
                except AttributeError: #to handle None reference (switch currently not connected)
                    print(f"Switch {dpid} seems to be not connected or not registered in the network")
            time.sleep(self.__MONITORING_INTERVAL) #thread sleeps for a period in between requests

            #Adaptive monitoring period algorithm
            alpha=0.5 #coefficient weighting average load and maximum load in the network overall load estimate
            loads=self.__link_df['congestion'] #congestion load for all network's links
            assert all(0<=load<=1 for load in loads), "Some congestion loads exceed the interval [0,1]"

            try:
                average_load=loads.mean() #average link's congestion load
            except (ZeroDivisionError, ValueError): #this happens when all links are down, or if the topology has been dismantled
                average_load=0
            try:
                max_load=loads.max() #maximum link congestion load
            except ValueError: #this happens when all links are down, or if the topology has been dismantled
                max_load=0
            network_load=alpha*average_load+(1-alpha)*max_load #estimate of network's overall congestion load
            print(f"average link load: {average_load}, max link load: {max_load}, network_load: {network_load}")
            self.__MONITORING_INTERVAL=-self.__BASE_INTERVAL*math.log2(network_load) #dynamically change monitoring period according to network's load
            if self.__MONITORING_INTERVAL<self.__MIN_INTERVAL: #if monitoring interval is decreasing below a set lower-bound
                self.__MONITORING_INTERVAL=self.__MIN_INTERVAL #set monitoring interval to lower-bound
            elif self.__MONITORING_INTERVAL>self.__MAX_INTERVAL: #if monitoring interval is increasing over a set upper-bound
                self.__MONITORING_INTERVAL=self.__MAX_INTERVAL #set monitoring interval to upper-bound
            self.__QUERY_COUNT+=1 #increment counter of port stats queries to switches
            print("New monitoring interval: ", self.__MONITORING_INTERVAL)
            print('\n')

    '''Thread function periodically refreshing flow tables and group tables of OVS switches by proactively recomputing static ECMP routes and broadcast routes 
       over the overlay graph (graph takes into account failed switches and links). Refreshing is operated every 180 seconds (default flow rules and broadcast 
       rules expire every 200 seconds)
       @param ECMP13 object'''
    def recompute_paths(self):
        while self.__firstConnection: #thread waits until network boot-up is completed (__firstConnection==False)
            time.sleep(5) #check value of flag __firstConnection every 5 seconds
        while not self.__firstConnection: #after network boot-up, periodically refresh proactive flow rules
            time.sleep(180) #waiting 180 seconds
            self.install_proactive(modify=True) #refresh default proactive unicast flow rules (static ECMP)
            self.proactive_broadcast(modify=True) #refresh proactive broadcast flow rules and group rules
            if len(self.graph.nodes)==0: #if the overlay graph is empty, the network has been shut down, so thread needs to terminate
                with open(log_path, "a") as log_file:
                    log_file.write(f'{dt.now()} -> Network has shut down, refresh thread terminates\n')
                return

    ######################################################################################################Event Handlers
    '''Handle OF FeaturesReply message from connecting OVS switch (from HANDSHAKE_DISPATCHER to CONFIG_DISPATCHER) and install on switch flow rule for table-miss
       and flow rule for marked packets (DS=00001100)
       @param ECMP13 object
       @param EventOFPSwitchFeatures event'''
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath=ev.msg.datapath #get datapath instance (OVS switch) associated with event
        with open(log_path, "a") as log_file:
            log_file.write(f"{dt.now()} -> Install table-miss on connected switch {self.__topo.get_name(dpid=datapath.id)}(DPID={datapath.id})\n")
            log_file.write(f"\n")

        ofproto=datapath.ofproto #adopted OpenFlow protocol version
        parser=datapath.ofproto_parser #to create OF messages
        match=parser.OFPMatch() #empty match, matches all flows
        actions=[parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)] #action: forward entire packet to controller's port
        self.add_flow(datapath, match, actions) #send FlowMod message to current OVS switch to install table-miss entry

        #Rule to match IPv4 packets with DSCP value 000011 (elephant flow notifications)
        switch_name=self.__topo.get_name(dpid=datapath.id) #name of the connecting switch
        if self.__topo.get_layer(switch_name)==FatTree.edge_layer(): #only if connecting switch is an edge, install rule for marked packets
            dscp_value=0b000011 ##DSCP value to match
            ipv4_match=parser.OFPMatch(eth_type=0x0800, ip_dscp=dscp_value) #match IPv4 packets with specific DSCP value
            ipv4_actions=[parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)] #action: forward entire packet to controller's port
            self.add_flow(datapath, ipv4_match, ipv4_actions, priority=100, idle_timeout=0, hard_timeout=0) #send FlowMod message to OVS switch to install rule
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Install default rule for marked packets on connected switch "
                               f"{self.__topo.get_name(dpid=datapath.id)}(DPID={datapath.id})\n")
                log_file.write(f"\n")

    '''Add/remove OVS switches as nodes in the overlay NetworkX graph when they enter/exit the network (from CONFIG_DISPATCHER to MAIN_DISPATCHER). Server nodes
       disconnection is also handled together with edge switch disconnection
       @param ECMP13 object
       @param EventDP dp'''
    @set_ev_cls(EventDP, MAIN_DISPATCHER)
    def handle_switch_enter(self, dp):
        datapath=dp.dp #get datapath instance (OVS switch) associated with event
        dpid=datapath.id #DPID of current OVS switch
        enter=dp.enter #flag: True if current OVS switch is entering the network, False if OVS switch is disconnecting
        ports_list=dp.ports #retrieves list of L2 ports available on current switch
        switch_name=self.__topo.get_name(dpid=dpid) #name of the current switch as registered in the fat-tree topology
        if enter: #if current switch is joining the network (flag True)
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Switch {switch_name}(DPID={dpid}) entered and its ports list is {ports_list}\n")
                log_file.write(f"\n")
            if dpid not in self.__datapaths.keys() or self.__datapaths[dpid] is None: #add OVS sw to dictionary when first connecting or after fail recovery
                self.__datapaths[dpid]=datapath #initialize reference to datapath object
                self.__broadcast_rules[dpid]=[] #<int, int[]>: key is switch's DPID, value is list of group IDs installed in switch's group table for broadcast
                self.__elephant_rules[dpid]=[] #<int, int[]>: key is switch's DPID, value is list of group IDs installed in switch's group table for elephants
            self.graph.add_nodes_from([(dpid, {'switch': datapath})]) #add current switch to overlay graph

        else: #if current switch is exiting the network (flag False)
            with open(log_path, "a") as log_file:
                log_file.write(f'{dt.now()} -> Switch {switch_name}(DPID={dpid}) exiting the network\n')
            if self.__topo.get_layer(switch_name)==FatTree.edge_layer(): #if exiting switch is edge, remove links between switch and servers from overlay graph
               servers=[self.__topo.get_mac(name=s) for s in self.__topo.get_down_nodes(switch_name)
                        if self.graph.has_node(self.__topo.get_mac(name=s))] #currently-active servers connected to exiting edge switch
               for server in servers:
                   if self.graph.has_edge(dpid, server): #if the link exiting switch->server is currently up
                       self.graph.remove_edge(dpid, server) #remove exiting switch-server link in networkx graph
                       self.graph.remove_node(server) #remove server from networkx overlay graph (if the dge switch is down, server is unreachable)
                       self.__servers[server]=None #remove reference to Host object from dictionary
                       with open(log_path, "a") as log_file:
                           log_file.write(f'{dt.now()} -> Removed link between switch {switch_name}(DPID={dpid}) and server '
                                          f'{self.__topo.get_name(mac=server)}({server})\n')
                           log_file.write(f'{dt.now()} -> Server {self.__topo.get_name(mac=server)}({server}) is unreachable, disconnected\n')

            self.graph.remove_node(dpid) #remove exiting switch from overlay graph
            self.__datapaths[dpid]=None #remove reference to datapath object from dictionary
            with open(log_path, "a") as log_file:
                log_file.write(f'\n')

    '''Add bidirectional edge to the graph when a new link between switches is detected (LLDP event)
       @param ECMP13 object
       @param EventLinkAdd ev'''
    @set_ev_cls(EventLinkAdd)
    def event_link_add_handler(self, ev):
        link=ev.link #get reference to Link object: Link Port<int dpid, int port_no, LIVE> to Port<int dpid, int port_no, LIVE>
        with open(log_path, "a") as log_file:
            log_file.write(f"{dt.now()} -> Link from {self.__topo.get_name(dpid=link.src.dpid)}({link.src}) "
                           f"to {self.__topo.get_name(dpid=link.dst.dpid)}({link.dst})\n")
            log_file.write(f"\n")

        src_dpid=link.src.dpid #DPID of source switch
        dst_dpid=link.dst.dpid #DPID of destination switch
        self.graph.add_edge(src_dpid, dst_dpid, weight=1) #add src-dst link in networkx graph with weight 1 (one hop)

    '''Remove bidirectional edge from the graph when failure of link between switches is detected (PortStatus change or LLDP timeout)
       @param ECMP13 object
       @param EventLinkAdd ev'''
    @set_ev_cls(EventLinkDelete)
    def event_link_del_handler(self, ev):
        link=ev.link #get the reference to the Link object
        src_dpid=link.src.dpid #DPID of source switch
        dst_dpid=link.dst.dpid #DPID of destination switch
        if self.graph.has_edge(src_dpid, dst_dpid): #if src-dst link is present in the NetworkX graph
            self.graph.remove_edge(src_dpid, dst_dpid) #remove src-dst link in networkx graph
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> DELETE link from {self.__topo.get_name(dpid=link.src.dpid)}({link.src}) "
                               f"switch to {self.__topo.get_name(dpid=link.dst.dpid)}({link.dst})\n")
                log_file.write(f"\n")

    '''Add host nodes in the graph when servers (host devices) join the network. If network boot-up is completed, it triggers proactive computation of default 
       unicast routing paths between each pair of servers in the network (static ECMP) and broadcast rules. Default flow rules and broadcast rules are installed 
       proactively on OVS switches
       @param ECMP13 object
       @param EventHostAdd ev'''
    @set_ev_cls(EventHostAdd)
    def event_host_add_handler(self, ev):
        host=ev.host #Host object associated with the event: <Host<str mac, port=Port<int dpid, int port_no, LIVE>
        try:
            server_name=self.__topo.get_name(mac=host.mac) #name of connecting server
            if server_name not in self.__topo.get_layer_nodes(FatTree.server_layer()):
                raise AttributeError
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Server {server_name}({host.mac}) is connecting to switch "
                               f"{self.__topo.get_name(dpid=host.port.dpid)}({host.port.dpid})\n")
                log_file.write(f"\n")

            self.graph.add_nodes_from([(host.mac, {'host': host})]) #it adds server node to overlay graph (key is server's MAC)
            self.graph.add_edge(host.mac, host.port.dpid, weight=1) #it adds server-edge switch link in networkx graph with weight 1 (one hop)
            if host.mac not in self.__servers.keys() or self.__servers[host.mac] is None: #add server (host device) to server dictionary
                self.__servers[host.mac]=host #initialize reference to Host object in the dictionary

            #Proactive flow rules computation is triggered when: network is in boot-up phase (firstConnection==True), all expected switches have connected to the
            #controller, all expected servers (host devices) are active, and all expected links have been discovered
            if (self.__firstConnection and len(self.__topo.switches())==len(self.__datapaths) and
                    len(self.__topo.hosts())==len(self.__servers) and len(self.__topo.links())==len(self.graph.edges)):
                self.__firstConnection=False #boot-up procedure is terminated
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Network boot-up completed, overlay graph computed\n")
                    log_file.write(f"{dt.now()} -> OVS switches connected: {self.__datapaths}\n")
                    log_file.write(f"{dt.now()} -> Number of connected switches: {len(self.__datapaths)}\n")
                    log_file.write(f"{dt.now()} -> Server connected: {self.__servers}\n")
                    log_file.write(f"{dt.now()} -> Number of connected servers (host devices): {len(self.__servers)}\n")
                    log_file.write(f"{dt.now()} -> Overlay nodes: {self.graph.nodes}\n")
                    log_file.write(f"{dt.now()} -> Number of nodes: {len(self.graph.nodes)}\n")
                    log_file.write(f"{dt.now()} -> Overlay edges: {self.graph.edges}\n")
                    log_file.write(f"{dt.now()} -> Number of edges: {len(self.graph.edges)}\n")
                    log_file.write(f"\n")

                self.install_proactive() #computes paths and installs default unicast flow rules proactively (static ECMP)
                self.proactive_broadcast() #computes and installs broadcast flow rules and group rules
        except AttributeError:
            print(f"Unauthorized host {host}({host.mac}) attempted connecting to controller. Stopped")

    '''Called when an OVS switch sends an OF Packet-In to the controller. In our DCN, switches may do this for:
            1)  LLDP events;
            2)  Matching flag packets to notify elephant flows discovery (only on edge switches);
            3)  Table-miss hit;
       @param ECMP13 object
       @param EventOFPPacketIn ev'''
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if self.__firstConnection:
            return #do not process Packet-Ins until network boot-up is completed
        if ev.msg.msg_len<ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes", ev.msg.msg_len, ev.msg.total_len)
        msg=ev.msg #get Packet-In message associated with event
        datapath=msg.datapath #OVS switch associated with event (datapath reference)
        assert datapath in self.__datapaths.values(), f"PacketIn received from unknown switch {datapath.id}"
        pkt=packet.Packet(msg.data) #message encapsulated in packet-In
        eth=pkt.get_protocols(ethernet.ethernet)[0] #get Ethernet frame from encapsulated packet
        if eth.ethertype==ether_types.ETH_TYPE_LLDP: #if L3 protocol is LLDP
            return #ignore LLDP packet (LLDP events handled by other functions)
        if eth.ethertype!=ether_types.ETH_TYPE_ARP and eth.ethertype!=ether_types.ETH_TYPE_IP:
            self.logger.debug(f"Unauthorized type of traffic {eth.ethertype}")
            return #we only provide flow rules for ARP traffic and IPv4 traffic
        elif eth.ethertype==ether_types.ETH_TYPE_ARP: #if L3 protocol is ARP
            pkt3=pkt.get_protocol(arp.arp) #get ARP packet (None if not ARP)
            src_ip=pkt3.src_ip #get source IPv4 address from packet
            dst_ip=pkt3.dst_ip #get destination IPv4 address from packet
            known_ipv4=[self.__topo.get_ipv4(name=server) for server in self.__topo.get_layer_nodes(FatTree.server_layer())] #all servers' IPv4s in the topology
            if src_ip not in known_ipv4:
                self.logger.debug(f"Unknown source IPv4 {src_ip}")
                return
            if dst_ip not in known_ipv4:
                self.logger.debug(f"Unknown destination IPv4 {dst_ip}")
                return
        else: #eth.ethertype==ether_types.ETH_TYPE_IP (L3 protocol is IPV4)
            pkt3=pkt.get_protocol(ipv4.ipv4) #get IPv4 packet (None if not IPv4)
            src_ip=pkt3.src #get source IPv4 address from packet
            dst_ip=pkt3.dst #get destination IPv4 address from packet
            known_ipv4=[self.__topo.get_ipv4(name=server) for server in self.__topo.get_layer_nodes(FatTree.server_layer())] #all servers' IPv4s in the topology
            if src_ip not in known_ipv4:
                self.logger.debug(f"Unknown source IPv4 {src_ip}")
                return
            if dst_ip not in known_ipv4:
                self.logger.debug(f"Unknown destination IPv4 {dst_ip}")
                return
            if dst_ip==self.__broadcastAddress: #if the packet is a broadcast packet
                self.logger.debug(f"Broadcast packet")
                return #broadcast packets will always be handled proactively, without control loop
            dscp_value=pkt3.tos>>2 #Extract DSCP value from the TOS field of the encapsulated IPv4 packet (upper 6 bits)
            self.logger.debug(f"IPv4 packet DSCP value: {dscp_value:06b} (decimal: {dscp_value})")
            if dscp_value==0b000011: #Check if the DSCP value matches 000011 (encapsulated packet is notifying and elephant flow)
                l4_protocol=pkt3.proto #Level 4 protocol
                if l4_protocol==inet.IPPROTO_TCP:
                    pkt_tcp=pkt.get_protocol(tcp.tcp) #get TCP datagram (None if not TCP)
                    if pkt_tcp:
                        l4="TCP"
                        src_port=pkt_tcp.src_port #get L4 source port number
                        dst_port=pkt_tcp.dst_port #get L4 destination port number
                    else:
                        self.logger.debug(f"Malformed TCP packet")
                        return
                elif l4_protocol==inet.IPPROTO_UDP:
                    pkt_udp=pkt.get_protocol(udp.udp) #get UDP datagram (None if not UDP)
                    if pkt_udp:
                        l4="UDP"
                        src_port=pkt_udp.src_port #get L4 source port number
                        dst_port=pkt_udp.dst_port #get L3 destination port number
                    else:
                        self.logger.debug(f"Malformed UDP packet")
                        return
                else: #L4 protocol is neither TCP nor UDP
                    self.logger.debug(f"Unsupported L4 protocol: {l4_protocol}")
                    return

                self.logger.info(f"Packet with DSCP 000011 detected: src={src_ip}, dst={dst_ip}, l4 protocol={l4}, src_port={src_port}, dst_port={dst_port}")

                #We call a function to compute and install ad-hoc flow rules for the elephant flow. The elephant flow is identified by the 5-tuple:
                #<source IPv4, destination IPv4, L4 protocol, L4 source port number, L4 destination port number> of the flag packet
                self.route_elephant_flows(msg, src_ip, dst_ip, l4_protocol, l4, src_port, dst_port)
                return
        self.logger.debug("Packet seems correct, but for some reason table miss!")

    '''Called when an OVS switch sends an OF Port-Stats Reply to the controller (response to an OF Port-Stats Requests). For all currently active links in the
       network, it will compute and memorize current statistics about traffic load, resource utilization, and congestion
       @param ECMP13 object
       @param EventOFPPortStatsReply ev'''
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        alpha=0.7 #coefficient weighting current statistics and previous congestion state when estimating a link's congestion state
        beta=0.5 #coefficient weighting link's current bandwidth utilization and port queue's occupation when estimating a link's congestion state

        dpid=ev.msg.datapath.id #datapath ID (int) of current switch (associated with reply message)
        switch_name=self.__topo.get_name(dpid=dpid) #name (string) of current switch

        body=ev.msg.body #content of reply message
        for stat in body: #for the statistics of each L2 port of current switch
            if stat.port_no>self.__k: #if L2 port number is higher than k, this means that port stats refer to controller port
                continue #ignore controller port
            if self.__topo.get_layer(switch_name)!=self.__topo.core_layer() and stat.port_no>(self.__k//2): #if we are on an edge or aggregation switch
                continue #look only the stats of downward L2 ports of current switch, skip upward L2 ports

            neighbor=[n for n in self.__topo.get_down_nodes(switch_name) if self.__topo.port(switch_name, n)[0]==stat.port_no] #downward neighbor for current port
            assert len(neighbor)==1 #only one neighbor can be reached from a single L2 port on current OVS switch

            link_name=neighbor[0]+"-"+switch_name #link name is a string "nameNeighborNode-nameCurrentSwitch"
            interfaces=[switch_name+'-eth'+str(stat.port_no)] #name of L2 ports at both ends of the link (we first add port name on current switch end)
            if self.__topo.get_layer(neighbor[0])!=self.__topo.server_layer(): #if the neighbor is another switch node
                interfaces.append(neighbor[0]+'-eth'+str(self.__topo.port(switch_name, neighbor[0])[1])) #port name on opposite end (if not server)
                neighbor_id=ECMP13.int_dpid(self.__topo.get_dpid(name=neighbor[0])) #datapath ID (int) of neighbor switch
            else: #if the neighbor is a server, we do not inspect the queue on link's server-end
                neighbor_id=self.__topo.get_mac(name=neighbor[0]) #MAC (string) of neighbor server

            if not self.graph.has_edge(dpid, neighbor_id): #if the link between current switch and neighbor node is not currently active in the network
                continue #try next link

            backlogs=[] #queue occupation at both ends of the link (just on switch end if the link is server-edge)
            dropped_packets=[] #dropped packets at both ends of the link (just on switch end if the link is server-edge)
            try:
                for interface in interfaces: #for all L2 interfaces of the link
                    found_backlog=False #flag
                    found_dropped=False #flag
                    result=subprocess.run(["sudo", "tc", "-s", "qdisc", "show", "dev", interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          text=True, check=True) #TC command to query L2 interfaces of the link for queue occupation and dropped packets
                    output=result.stdout #output of TC command
                    for line in output.splitlines(): #parsing the output line by line
                        if "dropped" in line: #extract dropped packets details from line
                            parts=line.split() #split the line
                            for part in parts:
                                if part.endswith(','): #look for the dropped packet field (e.g., 'dropped 10,')
                                    dropped_packets.append(int(part[:-1])) #remove the trailing ',' and convert to integer
                                    found_dropped=True
                                    break
                        if "backlog" in line: #extract backlog details from line
                            parts=line.split() #split the line
                            for part in parts:
                                if part.endswith('p'): #look for the backlog packet field (e.g., '10p')
                                    backlogs.append(int(part[:-1])) #remove the trailing 'p' and convert to integer
                                    found_backlog=True
                                    break
                        if found_backlog and found_dropped: #if both flags are True, inspection of TC output can be stopped
                            break
                print(f"{link_name} -> {interfaces}: Backlogs {backlogs} - Dropped {dropped_packets}")
            except subprocess.CalledProcessError as e:
                print(f"Error querying TC stats: {e.stderr}")

            current_row={'link_name': link_name,
                         'tx_packets': stat.tx_packets, #packets transmitted from upward link interface (from OF Port-Stats Reply)
                         'rx_packets': stat.rx_packets, #packets received on upward link interface (from OF Port-Stats Reply)
                         'tx_bytes': stat.tx_bytes, #bytes transmitted from upward link interface (from OF Port-Stats Reply)
                         'rx_bytes': stat.rx_bytes, #byte Received on upward link interface (from OF Port-Stats Reply)
                         'dropped_packets':dropped_packets, #on both link L2 interfaces (from TC)
                         'backlogs' : backlogs, #on both link L2 interfaces (from TC)
                         'utilization': 0, #initialize link utilization rate
                         'occupation': 0, #initialize link port buffer occupation rate
                         'congestion': 0, #initialize link congestion rate
                         'date': dt.now(),
                         'timestamp': time.time(),
                         'query_count': self.__QUERY_COUNT} #dictionary containing current stats for the link

            try:
                if len(self.__link_df)>0 and not self.__link_df[self.__link_df['link_name']==current_row['link_name']].empty:
                    #if in the dataframe containing current link stats there is already a row corresponding to current link

                    prev_row=self.__link_df.loc[self.__link_df['link_name']==current_row['link_name']].iloc[0] #extract current link's row from dataframe

                    if current_row['tx_bytes']+current_row['rx_bytes']-prev_row['tx_bytes']-prev_row['rx_bytes']<0: #if the link has failed from last query
                        data_load=current_row['tx_bytes']+current_row['rx_bytes'] #data transmitted on the link in last query interval
                    else: #if the link has not failed from last query
                        data_load=(current_row['tx_bytes']+current_row['rx_bytes']-prev_row['tx_bytes']-prev_row['rx_bytes']) #data transmitted on the link
                    period=current_row['timestamp']-prev_row['timestamp'] #query interval [s]
                    throughput=data_load*8/period #portion of link's bandwidth utilized in the last query interval [Mbps]
                    utilization=throughput/(self.__bw[0]*(10**6)) #current utilization rate of the link
                    if utilization<0.01:
                        current_row['utilization']=0.01
                    elif utilization>1:
                        current_row['utilization']=1
                    else:
                        current_row['utilization']=utilization #keep utilization rate in the [0.01, 1] interval

                    if sum(current_row['dropped_packets'])-sum(prev_row['dropped_packets'])>=0: #if the link has not failed from last query
                        for i in range(len(current_row['dropped_packets'])): #for both link's L2 interfaces
                            current_row['dropped_packets'][i]-=prev_row['dropped_packets'][i] #packets dropped on the link on the last query interval

                    occupation=sum(backlogs)/(self.__max_queue[0]*len(backlogs)) #overall current queue occupation at link's ends
                    if occupation<0.01:
                        current_row['occupation']=0.01
                    elif occupation>1:
                        current_row['occupation']=1
                    else:
                        current_row['occupation']=occupation #keep port buffer occupation in the [0.01, 1] interval

                    #compute current congestion level for the current link
                    congestion=alpha*(beta*current_row['utilization']+(1-beta)*current_row['occupation'])+(1-alpha)*prev_row['congestion']
                    if congestion<0.01:
                        current_row['congestion']=0.01
                    else:
                        current_row['congestion']=congestion #keep congestion rate in the [0.01, 1] interval

                    if current_row['tx_bytes']+current_row['rx_bytes']-prev_row['tx_bytes']-prev_row['rx_bytes']<0: #if link has been just reactivated
                        current_row['congestion']=current_row['congestion']-(current_row['congestion']*0.9) #reduce congestion level of 90% (bias)

                    self.__link_df.drop(self.__link_df[self.__link_df['link_name']==current_row['link_name']].index, inplace=True) #remove old data from dataframe
                    new_df=pd.DataFrame([current_row]) #convert new data about current link to dataframe type
                    self.__link_df=pd.concat([self.__link_df, new_df], ignore_index=True) #append new data about current link to the stats dataframe
                    #ECMP13.export_stats(new_df, "LinkStatsEnhanced.csv") #save new link data on .csv file (enhanced controller)
                    #ECMP13.export_stats(new_df, "LinkStatsGreedy.csv") #save new link data on .csv file (enhanced controller + greedy heuristic)
                    ECMP13.export_stats(new_df, "LinkStatsProb.csv") #save new link data on .csv file (enhanced controller + probabilistic heuristic)

                else: #if no row for the current link is present in the p dataframe (it's the first time we are querying port stats or if the current link
                      #was down and then has been reactivated). Previous data are assumed to be 0

                    data_load=(current_row['tx_bytes']+current_row['rx_bytes']) #data transmitted on the link in the last query interval
                    period=self.__MONITORING_INTERVAL #query interval [s]
                    throughput=data_load*8/period #portion of link's bandwidth utilized in the last query interval [Mbps]
                    utilization=throughput/(self.__bw[0]*(10**6)) #current utilization rate of the link
                    if utilization<0.01:
                        current_row['utilization']=0.01
                    elif utilization>1:
                        current_row['utilization']=1
                    else:
                        current_row['utilization']=utilization #keep current utilization rate in the [0.01, 1] interval

                    occupation=sum(backlogs)/(self.__max_queue[0]*len(backlogs)) #current overall port queue occupation at link's ends
                    if occupation<0.01:
                        current_row['occupation']=0.01
                    elif occupation>1:
                        current_row['occupation']=1
                    else:
                        current_row['occupation']=occupation #keep current occupation rate in the [0.01, 1] interval

                    #compute current congestion level for the current link
                    link_congestion=0.01 #previous link congestion level (assumed idle)
                    congestion=alpha*(beta*current_row['utilization']+(1-beta)*current_row['occupation'])+(1-alpha)*link_congestion
                    if congestion<0.01:
                          current_row['congestion']=0.01
                    else:
                          current_row['congestion']=congestion #keep current congestion rate in the [0.01, 1] interval

                    if current_row['query_count']>1: #if the link has just been reactivated
                          current_row['congestion']=current_row['congestion']-(current_row['congestion']*0.9) #reduce congestion of 90% (bias)

                    new_df=pd.DataFrame([current_row]) #convert new data about current link to DataFrame object
                    self.__link_df=pd.concat([self.__link_df, new_df], ignore_index=True) #append new data about current link to the stats dataframe
                    #ECMP13.export_stats(new_df, "LinkStatsEnhanced.csv") #save new link data on .csv file (enhanced controller)
                    #ECMP13.export_stats(new_df, "LinkStatsGreedy.csv") #save new link data on .csv file (enhanced controller + greedy heuristic)
                    ECMP13.export_stats(new_df, "LinkStatsProb.csv") #save new link data on .csv file (enhanced controller + probabilistic heuristic)

            except KeyError:
                print('KeyError: invalid key specified for either dataframe or dictionary')
            except IndexError:
                print('IndexError: trying to perform operation on empty row')

    ####################################################################################OF Control and Routing Functions
    '''Compute proactively default paths for unicast flows between each pair of servers in the data center network, according to static ECMP routing:
        1) Check from the overlay graph if a server is currently active (avoid computing routes for inactive servers);
        2) Compute all equal cost paths existing between source and destination servers (identified by their MACs) on the overlay graph (avoiding disabled 
           switches and failed links) using all_shortest_path() function of NetworkX library. Paths are weighted in number of hops. Paths are returned as 
           list of all traversed nodes, identified by MACs (source and destination) and integer DPIDs (switches);
        3) Compute an hashing value and use it to select a specific path between those returned by NetworkX with a mod-N operation;
        4) For every switch in the path:
            4.1) Compute static port mapping with next switch using custom function from our custom FatTree class;
            4.2) If static ARP is not enabled on servers, define matching for source-destination ARP traffic and install flow rule on current switch;
            4.3) Define matching for source-destination IPv4 traffic and install flow rule on current switch;
       @param ECMP13 object
       @param bool modify (True if the function is refreshing flow rules, False if it is installing them for the first time)'''
    def install_proactive(self, modify=False):
        if modify:
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Validity interval expired, refreshing flow rules for unicast IPv4 traffic\n")
                log_file.write(f"{dt.now()} -> OVS switches connected: {self.__datapaths}\n")
                log_file.write(f"{dt.now()} -> Number of connected switches: {len([dp for dp in self.__datapaths.values() if dp is not None])}\n")
                log_file.write(f"{dt.now()} -> Server connected: {self.__servers}\n")
                log_file.write(f"{dt.now()} -> Number of connected servers (host devices): {len(self.__servers)}\n")
                log_file.write(f"{dt.now()} -> Overlay nodes: {self.graph.nodes}\n")
                log_file.write(f"{dt.now()} -> Number of nodes: {len(self.graph.nodes)}\n")
                log_file.write(f"{dt.now()} -> Overlay edges: {self.graph.edges}\n")
                log_file.write(f"{dt.now()} -> Number of edges: {len(self.graph.edges)}\n")
                log_file.write(f"\n")
        else:
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Network boot up completed, starting path computation installation of proactive flow rules\n")

        servers=[h for h in self.__topo.get_layer_nodes(FatTree.server_layer()) if self.graph.has_node(self.__topo.get_mac(name=h))] #currently active servers
        for src_server in servers: #for every possible source server
            for dst_server in servers: #for every possible destination server
                if src_server==dst_server: #no need to compute a loopback path
                    continue #move to next destination server

                src_mac=self.__topo.get_mac(name=src_server) #MAC address of source server
                dst_mac=self.__topo.get_mac(name=dst_server) #MAC address of destination server
                paths=[]
                try:
                    paths=list(nx.all_shortest_paths(self.graph, src_mac, dst_mac, weight="weight")) #compute all equal-cost paths from src to dst in our DCN
                except nx.exception.NodeNotFound:
                    print(f"Either source {src_mac} or destination {dst_mac} are invalid")
                except nx.exception.NetworkXNoPath:
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> No path exists between {src_server} and {dst_server}\n")
                        log_file.write(f"\n")

                flow_hash=hash(src_mac+dst_mac) #hashing value computed over MAC addresses of source and destination hosts
                path_num=int(flow_hash%len(paths)) #mod-N operation returning index of selected path
                selected_path=paths[path_num] #chosen path among equal-cost alternatives between source and destination
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Equal cost paths between {src_server} and {dst_server}: "
                                       f"{paths}. Number of paths: {len(paths)}. Paths length: {[len(path)-1 for path in paths]}.\n")
                    log_file.write(f"{dt.now()} -> Selected path between {src_server} and {dst_server}: "
                                       f"{selected_path}. Path length: {len(selected_path)-1}.\n")
                    log_file.write(f"\n")

                src_ip=self.__topo.get_ipv4(name=src_server) #IPv4 address of source server
                dst_ip=self.__topo.get_ipv4(name=dst_server) #IPv4 address of destination server
                in_port=0 #ingress port initialization
                port_succession=[] #list of tuples (int exit_port, int ingress_port) for traversed links in the selected path
                for i,node in enumerate(selected_path): #for every node in the selected path
                    if i==0: #current node is source server (first in the path)
                        node_name=self.__topo.get_name(mac=node) #fecth source server name
                        assert isinstance(selected_path[i+1], int) #the next node is an edge switch, so the successor in the path must be an integer DPID
                        connected_edge=self.__topo.get_name(dpid=selected_path[i+1]) #fetch edge switch name (next node)
                        port_succession.append(self.__topo.port(node_name, connected_edge)) #port mapping between source server and edge switch
                        in_port=self.__topo.port(node_name, connected_edge)[1] #set input port for edge switch

                    elif i==len(selected_path)-2: #current node is edge switch serving destination server (second last in the path)
                        assert isinstance(node, int) #the current element in the path must be an integer DPID
                        node_name=self.__topo.get_name(dpid=node) #fetch edge switch name
                        assert isinstance(selected_path[i+1], str) #the next element in the path must be a string MAC (corresponding to destination server)
                        destination=self.__topo.get_name(mac=selected_path[i+1]) #fetch destination server name (next node)
                        port_succession.append(self.__topo.port(node_name, destination)) #port mapping between edge switch and destination server
                        out_port=self.__topo.port(node_name, destination)[0] #exit port for edge switch

                        try:
                            switch=self.__datapaths[node] #reference to datapath object (edge OVS switch where to install the flow rule)
                            ofp_parser=switch.ofproto_parser #to create OpenFlow messages
                            actions=[ofp_parser.OFPActionOutput(out_port)] #action: output message out of specified port
                            if not self.__static_arp: #if static ARP is not enabled, install flow rules for ARP traffic between source and destination
                                match_arp=ofp_parser.OFPMatch(eth_type=0x0806, in_port=in_port, eth_src=src_mac, arp_spa=src_ip, arp_tpa=dst_ip) #ARP match
                                self.add_flow(datapath=switch, match=match_arp, actions=actions, priority=5, hard_timeout=200) #install ARP rule
                            match=ofp_parser.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ip, ipv4_dst=dst_ip) #IPv4 traffic match
                            self.add_flow(datapath=switch, match=match, actions=actions, priority=10, hard_timeout=200) #install flow rule
                            break #flow rules have been installed in all switches of the path
                        except KeyError:
                            print(f'Specified DPID {node} does not correspond to any switch in the topology')

                    else: #for every other switch node traversed in the path
                        assert isinstance(node, int) #the current element in the path must be an integer DPID (switch)
                        node_name=self.__topo.get_name(dpid=node) #fetch current switch name
                        assert isinstance(selected_path[i+1], int) #next path element must be an int DPID (next switch)
                        next_switch=self.__topo.get_name(dpid=selected_path[i+1]) #fetch next switch name
                        port_succession.append(self.__topo.port(node_name, next_switch)) #port mapping between current switch and next switch
                        out_port=self.__topo.port(node_name, next_switch)[0] #exit port for current switch

                        try:
                            switch=self.__datapaths[node] #reference to current datapath object (OVS switch where to install the flow rule)
                            ofp_parser=switch.ofproto_parser #to create OpenFlow messages
                            actions=[ofp_parser.OFPActionOutput(out_port)] #action: output message out of specified port
                            if not self.__static_arp: #if static ARP is not enabled, install flow rules for ARP traffic between source and destination
                                match_arp=ofp_parser.OFPMatch(eth_type=0x0806, in_port=in_port, eth_src=src_mac, arp_spa=src_ip, arp_tpa=dst_ip) #ARP match
                                self.add_flow(datapath=switch, match=match_arp, actions=actions, priority=5, hard_timeout=200) #install ARP rule
                            match=ofp_parser.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ip, ipv4_dst=dst_ip) #IPv4 traffic match
                            self.add_flow(datapath=switch, match=match, actions=actions, priority=10, hard_timeout=200) #install flow rule
                        except KeyError:
                            print(f'Specified DPID {node} does not correspond to any switch in the topology')
                        in_port=self.__topo.port(node_name, next_switch)[1] #progress ingress port for next switch in the path

                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Path between {src_server} and {dst_server} installed. Number of hops: {len(selected_path)-1}.\n")
                    log_file.write(f"{dt.now()} -> Port succession in the path: {port_succession}\n")
                    log_file.write(f"\n")

        with open(log_path, "a") as log_file:
            log_file.write(f"{dt.now()} -> Computation of unicast IPv4 rules finished #######################################################################.\n")
            log_file.write(f"\n")

    '''Installs proactively flow rules for IPv4 broadcasting in the data center on each switch currently active. Installed rules are as follows:
          1)On an edge switch, if the broadcast message comes in on a downward port (from a server), flood down to all other downward ports (other servers), then 
            select a single upward port to forward up to a currently active aggregation switch;
          2)On an edge switch, if the broadcast message comes in on a upward port (from an agg switch), flood down to all downward ports (to servers);
          3)On an agg switch, if the broadcast message comes in on a downward port (from an edge switch), flood down to all other downward ports (other edge
            switches), then select a single upward port to forward up to a currently active core switch;
          4)On an agg switch, if the broadcast message comes in on a upward port (from a core switch), flood down to all downward ports (to edge switches);
          5)On a core switch, when a broadcast message comes in on a downward port (from an agg switch), flood down to other downward ports (other agg switches);
       Forwarding packets out of multiple ports is achieved by installing group rules ALL on the switches' group tables before installing broadcast flow rules.
       Selected upward port is the one with current lowest congestion rate on the switch. Broadcast rules are always computed on the overlay graph, in order to 
       avoid failed links/switches. Forwarding broadcast messages out of a single upward port in edge switches and agg switches prevent servers from receiving 
       duplicated messages from multiple paths'
       @param ECMP13 object
       @param bool modify (True if the function is refreshing flow rules, False if it is installing them for the first time)'''
    def proactive_broadcast(self, modify=False):
        if modify:
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Validity interval expired, refreshing IPv4 broadcast flow rules\n")
                log_file.write(f"{dt.now()} -> OVS switches connected: {self.__datapaths}\n")
                log_file.write(f"{dt.now()} -> Number of connected switches: {len([dp for dp in self.__datapaths.values() if dp is not None])}\n")
                log_file.write(f"{dt.now()} -> Server connected: {self.__servers}\n")
                log_file.write(f"{dt.now()} -> Number of connected servers (host devices): {len(self.__servers)}\n")
                log_file.write(f"{dt.now()} -> Overlay nodes: {self.graph.nodes}\n")
                log_file.write(f"{dt.now()} -> Number of nodes: {len(self.graph.nodes)}\n")
                log_file.write(f"{dt.now()} -> Overlay edges: {self.graph.edges}\n")
                log_file.write(f"{dt.now()} -> Number of edges: {len(self.graph.edges)}\n")
                log_file.write(f"\n")
        else:
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Network boot up completed, installing proactive flow rules for data center IPv4 broadcast\n")
                log_file.write(f"{dt.now()} -> OVS switches connected: {self.__datapaths}\n")
                log_file.write(f"{dt.now()} -> Number of connected switches: {len([dp for dp in self.__datapaths.values() if dp is not None])}\n")
                log_file.write(f"{dt.now()} -> Server connected: {self.__servers}\n")
                log_file.write(f"{dt.now()} -> Number of connected servers (host devices): {len(self.__servers)}\n")
                log_file.write(f"{dt.now()} -> Overlay nodes: {self.graph.nodes}\n")
                log_file.write(f"{dt.now()} -> Number of nodes: {len(self.graph.nodes)}\n")
                log_file.write(f"{dt.now()} -> Overlay edges: {self.graph.edges}\n")
                log_file.write(f"{dt.now()} -> Number of edges: {len(self.graph.edges)}\n")
                log_file.write(f"\n")

        #get list of all edge switches currently active in the network
        edge_switches=[sw for sw in self.__topo.get_layer_nodes(FatTree.edge_layer()) if self.graph.has_node(ECMP13.int_dpid(self.__topo.get_dpid(name=sw)))]

        #get list of all agg switches currently active in the network
        agg_switches=[sw for sw in self.__topo.get_layer_nodes(FatTree.agg_layer()) if self.graph.has_node(ECMP13.int_dpid(self.__topo.get_dpid(name=sw)))]

        #get list of all core switches currently active in the network
        core_switches=[sw for sw in self.__topo.get_layer_nodes(FatTree.core_layer()) if self.graph.has_node(ECMP13.int_dpid(self.__topo.get_dpid(name=sw)))]

        for edge in edge_switches: #for all edge switches in the data center
            dpid=ECMP13.int_dpid(self.__topo.get_dpid(name=edge)) #DPID associated to current edge switch
            switch=None
            try:
                switch=self.__datapaths[dpid] #get datapath reference to current edge switch
            except AttributeError:
                print(f'Switch {edge}(DPID={dpid}) seems to be disconnected or not correctly registered')
            ofproto=switch.ofproto #OpenFlow 1.3
            ofp_parser=switch.ofproto_parser #manage OF messages

            if modify and len(self.__broadcast_rules[dpid])>0: #if we are refreshing broadcast rules and some broadcast group rules are saved on the switch
                for group in self.__broadcast_rules[dpid]: #for all memorized group ID
                    del_req=ofp_parser.OFPGroupMod(datapath=switch, command=ofproto.OFPGC_DELETE, group_id=group) #remove rule from switch's group table
                    switch.send_msg(del_req) #controller sends GroupMod to current OVS switch
                self.__broadcast_rules[dpid]=[] #no group ID memorized in current switch

            for i in range(1, (self.__k//2)+1): #down ports of current edge switch (numbered from 1 to k/2)
                group_id=i #identify a unique set of output actions for broadcast packets coming from a specific down port
                exit_ports=[self.__topo.port(edge, n)[0] for n in self.__topo.get_down_nodes(edge)
                            if self.graph.has_edge(ECMP13.int_dpid(self.__topo.get_dpid(name=edge)), self.__topo.get_mac(name=n)) and
                              self.__topo.port(edge, n)[0]!=i] #initialize exit ports by adding all active down ports
                up_neigh=[n for n in self.__topo.get_up_nodes(edge) if
                          self.graph.has_edge(ECMP13.int_dpid(self.__topo.get_dpid(name=edge)), ECMP13.int_dpid(self.__topo.get_dpid(name=n)))]
                          #active up neighbors of current edge switch

                if len(exit_ports)==0 or len(up_neigh)==0:
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> No connection active on switch {edge}\n")
                        log_file.write(f"\n")
                    continue

                if modify: #if we are refreshing broadcast rules
                    link_names=[] #get name of all active upward links of the current switch
                    for neighbor in up_neigh:
                        link_names.append(f"{edge}-{neighbor}") #link name is a string "nameEdge-nameSwitch"

                    tmp_df=self.__link_df[self.__link_df["link_name"].isin(link_names)] #filter up-to-date stats about current switch's upward links
                    if not len(tmp_df)==0:
                        min_row=tmp_df.loc[tmp_df["congestion"].idxmin()] #get upward link with the lowest congestion rate
                        min_link=min_row["link_name"] #get link name
                        min_neigh=min_link.split('-')[1] #get upward neighbor name (single upward neighbor where to forward broadcast traffic)

                    else: #if no data is present in the dataframe, current edge switch has been brought up again after disconnection
                        h=hash(ECMP13.int_dpid(self.__topo.get_dpid(name=edge))) #hash-based selection
                        min_neigh=up_neigh[int(h % len(up_neigh))] #choose a single upward neighbor with mod-N operation

                    exit_ports.append(self.__topo.port(edge, min_neigh)[0]) #add port towards selected upward neighbor to exit ports list

                else: #if broadcast rules are being computed for the firs time
                    h=hash(ECMP13.int_dpid(self.__topo.get_dpid(name=edge))) #hash-based selection
                    selected=up_neigh[int(h%len(up_neigh))] #choose a single upward neighbor with mod-N operation
                    exit_ports.append(self.__topo.port(edge, selected)[0]) #add port towards selected upward neighbor to exit ports list

                buckets=[] #initialize bucket list of output actions for the group
                for port in exit_ports:
                    action=ofp_parser.OFPActionOutput(port) #action: forward out of specified port
                    buckets.append(ofp_parser.OFPBucket(actions=[action]))
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Broadcast instructions for edge switch {edge}(DPID={dpid}): broadcast address {self.__broadcastAddress}, "
                                   f"input port {edge}-eth{i}. Output ports: {exit_ports}. Output actions = {[bucket.actions for bucket in buckets]}\n")
                    log_file.write(f"\n")

                req=ofp_parser.OFPGroupMod(datapath=switch, command=ofproto.OFPFC_ADD, type_=ofproto.OFPGT_ALL, group_id=group_id, buckets=buckets) #GroupMod
                switch.send_msg(req) #controller sends GroupMod to current OVS switch to install group rule
                self.__broadcast_rules[dpid].append(group_id) #register memorized group ID for current edge switch

                match=ofp_parser.OFPMatch(eth_type=0x0800, in_port=i, ipv4_dst=self.__broadcastAddress) #matching for broadcast traffic
                actions=[ofp_parser.OFPActionGroup(group_id)] #action for OVS switch: forward out of all ports specified in the group
                self.add_flow(datapath=switch, match=match, actions=actions, priority=6, hard_timeout=200) #install broadcast flow rule

            for i in range((self.__k//2)+1, self.__k+1): #up ports of current edge switch (from k/2 to k)
                group_id=i #identify a unique set of output actions for broadcast packets coming from a specific up port
                exit_ports=[self.__topo.port(edge, n)[0] for n in self.__topo.get_down_nodes(edge)
                            if self.graph.has_edge(ECMP13.int_dpid(self.__topo.get_dpid(name=edge)), self.__topo.get_mac(name=n))] #all edge's downward ports
                if len(exit_ports)==0:
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> No downward connection active on switch {edge}\n")
                        log_file.write(f"\n")
                    continue

                buckets=[] #initialize bucket list of output actions for the group
                for port in exit_ports: #for each exit port
                    action=ofp_parser.OFPActionOutput(port) #action: forward out of specified port
                    buckets.append(ofp_parser.OFPBucket(actions=[action]))
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Broadcast instructions for edge switch {edge}(DPID={dpid}): broadcast address {self.__broadcastAddress}, "
                                   f"input port {edge}-eth{i}. Output ports: {exit_ports}. Output actions = {[bucket.actions for bucket in buckets]}\n")
                    log_file.write(f"\n")

                req=ofp_parser.OFPGroupMod(datapath=switch, command=ofproto.OFPFC_ADD, type_=ofproto.OFPGT_ALL, group_id=group_id, buckets=buckets) #GroupMod
                switch.send_msg(req) #controller sends GroupMod to current OVS switch
                self.__broadcast_rules[dpid].append(group_id) #registers memorized group ID for current edge switch

                match=ofp_parser.OFPMatch(eth_type=0x0800, in_port=i, ipv4_dst=self.__broadcastAddress) #matching for broadcast traffic
                actions=[ofp_parser.OFPActionGroup(group_id)] #action for OVS switch: forward out of all ports specified in the group
                self.add_flow(datapath=switch, match=match, actions=actions, priority=6, hard_timeout=200) #install broadcast flow rule on current edge switch

        for agg in agg_switches: #for all agg switches in the data center
            dpid=ECMP13.int_dpid(self.__topo.get_dpid(name=agg)) #DPID associated to current agg switch
            switch=None
            try:
                switch=self.__datapaths[dpid] #get datapath reference for current agg switch
            except AttributeError:
                print(f'Switch {agg}(DPID={dpid}) seems to be disconnected or not correctly registered')
            ofproto=switch.ofproto #OpenFlow 1.3
            ofp_parser=switch.ofproto_parser #manage OF messages

            if modify and len(self.__broadcast_rules[dpid])>0: #if we are refreshing broadcast rules and group IDs have been memorized for current agg switch
                for group in self.__broadcast_rules[dpid]: #for each memorized group ID related to broadcast rules
                    del_req=ofp_parser.OFPGroupMod(datapath=switch, command=ofproto.OFPGC_DELETE, group_id=group) #clear group rule associated with group ID
                    switch.send_msg(del_req) #controller sends GroupMod to current OVS switch
                self.__broadcast_rules[dpid]=[] #remove memorized group ID for current OVS switch

            for i in range(1, (self.__k//2)+1): #down ports of current agg switch (from 1 to k/2)
                group_id=i #identify a unique set of output actions for broadcast packets coming from a specific down port
                exit_ports=[self.__topo.port(agg, n)[0] for n in self.__topo.get_down_nodes(agg)
                            if self.graph.has_edge(ECMP13.int_dpid(self.__topo.get_dpid(name=agg)), ECMP13.int_dpid(self.__topo.get_dpid(name=n))) and
                            self.__topo.port(agg, n)[0]!=i] #initialize exit ports by adding all active down ports
                up_neigh=[n for n in self.__topo.get_up_nodes(agg) if
                         self.graph.has_edge(ECMP13.int_dpid(self.__topo.get_dpid(name=agg)), ECMP13.int_dpid(self.__topo.get_dpid(name=n)))] #active up neighbors

                if len(exit_ports)==0 or len(up_neigh)==0:
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> No connection active on switch {agg}\n")
                        log_file.write(f"\n")
                    continue

                if modify: #if we are refreshing broadcast rules
                    link_names=[] #contain name of all currently active upward links of current agg switch
                    for neighbor in up_neigh: #for all upward neighbours
                        link_names.append(f"{agg}-{neighbor}") #link name is a string "nameAgg-nameSwitch"

                    tmp_df=self.__link_df[self.__link_df["link_name"].isin(link_names)] #filter up-to-date stats about current switch's upward links
                    if not len(tmp_df)==0:
                        min_row=tmp_df.loc[tmp_df["congestion"].idxmin()] #select upward link with minimum congestion rate
                        min_link=min_row["link_name"] #link of selected link
                        min_neigh=min_link.split('-')[1] #selected upward neighbor (broadcast traffic will be forwarded to it)

                    else: #if no data is present in the dataframe, this means that the switch has just been reactivated
                        h=hash(ECMP13.int_dpid(self.__topo.get_dpid(name=agg))) #hash-basd selection
                        min_neigh=up_neigh[int(h % len(up_neigh))] #choose a single upward neighbor with mod-N operation

                    exit_ports.append(self.__topo.port(agg, min_neigh)[0]) #add selected upward port to list of exit ports for current agg switch

                else: #if broadcast rules are being computed for the first time
                    h=hash(ECMP13.int_dpid(self.__topo.get_dpid(name=agg))) #hash-based selection
                    selected=up_neigh[int(h%len(up_neigh))] #choose a single upward neighbor with mod-N operation
                    exit_ports.append(self.__topo.port(agg, selected)[0]) #add selected upward port to list of exit ports for current agg switch

                buckets=[] #initialize bucket of output actions for the group
                for port in exit_ports: #for all selected exit ports
                    action=ofp_parser.OFPActionOutput(port) #action: forward out of specified port
                    buckets.append(ofp_parser.OFPBucket(actions=[action]))
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Broadcast instructions for agg switch {agg}(DPID={dpid}): broadcast address {self.__broadcastAddress}, "
                                   f"input port {agg}-eth{i}. Output ports: {exit_ports}. Output actions = {[bucket.actions for bucket in buckets]}\n")
                    log_file.write(f"\n")

                req=ofp_parser.OFPGroupMod(datapath=switch, command=ofproto.OFPFC_ADD, type_=ofproto.OFPGT_ALL, group_id=group_id, buckets=buckets) #GroupMod
                switch.send_msg(req) #controller sends GroupMod to current OVS switch
                self.__broadcast_rules[dpid].append(group_id) #register memorized group ID for current agg switch

                match=ofp_parser.OFPMatch(eth_type=0x0800, in_port=i, ipv4_dst=self.__broadcastAddress) #matching for broadcast traffic
                actions=[ofp_parser.OFPActionGroup(group_id)] #action for OVS switch: forward out of all ports specified in the group
                self.add_flow(datapath=switch, match=match, actions=actions, priority=6, hard_timeout=200) #install flow rule for broadcast traffic

            for i in range((self.__k//2)+1, self.__k+1): #up ports of current agg switch (numbered from k/2 to k)
                group_id=i #identify a unique set of output actions for broadcast packets coming from a specific upward port
                exit_ports=[self.__topo.port(agg, n)[0] for n in self.__topo.get_down_nodes(agg)
                            if self.graph.has_edge(ECMP13.int_dpid(self.__topo.get_dpid(name=agg)), ECMP13.int_dpid(self.__topo.get_dpid(name=n)))] #down pots

                if len(exit_ports)==0:
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> No downward connection active on switch {agg}\n")
                        log_file.write(f"\n")
                    continue

                buckets=[] #initialize bucket list of output actions for the group
                for port in exit_ports: #for all selected exit ports
                    action=ofp_parser.OFPActionOutput(port) #action: forward out of specified port
                    buckets.append(ofp_parser.OFPBucket(actions=[action]))
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Broadcast instructions for agg switch {agg}(DPID={dpid}): broadcast address {self.__broadcastAddress}, "
                                   f"input port {agg}-eth{i}. Output ports: {exit_ports}. Output actions = {[bucket.actions for bucket in buckets]}\n")
                    log_file.write(f"\n")

                req=ofp_parser.OFPGroupMod(datapath=switch, command=ofproto.OFPFC_ADD, type_=ofproto.OFPGT_ALL, group_id=group_id, buckets=buckets) #GroupMod
                switch.send_msg(req) #controller sends GroupMod to current OVS switch
                self.__broadcast_rules[dpid].append(group_id) #memorize group ID for current OVS switch

                match=ofp_parser.OFPMatch(eth_type=0x0800, in_port=i, ipv4_dst=self.__broadcastAddress) #matching for broadcast traffic
                actions=[ofp_parser.OFPActionGroup(group_id)] #action for OVS switch: forward out of all ports specified in the group
                self.add_flow(datapath=switch, match=match, actions=actions, priority=6, hard_timeout=200) #install flow rule for broadcast traffic on switch

        for core in core_switches: #for all core switches in the data center
            dpid=ECMP13.int_dpid(self.__topo.get_dpid(name=core)) #DPID associated to core switch
            switch=None
            try:
                switch=self.__datapaths[dpid] #get datapath reference to current core switch
            except AttributeError:
                print(f'Switch {core}(DPID={dpid}) seems to be disconnected or not correctly registered')

            ofproto=switch.ofproto #OpenFlow 1.3
            ofp_parser=switch.ofproto_parser #manage OF packets

            if modify and len(self.__broadcast_rules[dpid])>0: #if broadcast rules are being refreshed and some group ID are already memorized for current core
                for group in self.__broadcast_rules[dpid]: #for all memorized group IDs (for broadcast traffic)
                    del_req=ofp_parser.OFPGroupMod(datapath=switch, command=ofproto.OFPGC_DELETE, group_id=group) #remove group rule associated to group ID
                    switch.send_msg(del_req) #controller sends GroupMod to current OVS switch
                self.__broadcast_rules[dpid]=[] #remove memorized group ID for current OVS switch

            for i in range(1, self.__k+1): #down ports of current core switch (numbered from 1 to k)
                group_id=self.__k+i #identify a unique set of output actions for broadcast traffic coming from a specific downward port
                exit_ports=[self.__topo.port(core, n)[0] for n in self.__topo.get_down_nodes(core)
                            if self.graph.has_edge(ECMP13.int_dpid(self.__topo.get_dpid(name=core)), ECMP13.int_dpid(self.__topo.get_dpid(name=n))) and
                            self.__topo.port(core,n)[0]!=i] #forward broadcast packet out of all core's ports except ingress port i

                if len(exit_ports)==0:
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> No connection active on switch {core}\n")
                        log_file.write(f"\n")
                    continue

                buckets=[] #initialize bucket list of output actions for the group
                for port in exit_ports: #for all selected exit ports
                    action=ofp_parser.OFPActionOutput(port) #action: forward out of specified port
                    buckets.append(ofp_parser.OFPBucket(actions=[action]))
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Broadcast instructions for core switch {core}(DPID={dpid}): broadcast address {self.__broadcastAddress}, "
                                   f"input port {core}-eth{i}. Output ports: {exit_ports}. Output actions = {[bucket.actions for bucket in buckets]}\n")
                    log_file.write(f"\n")

                req=ofp_parser.OFPGroupMod(datapath=switch, command=ofproto.OFPFC_ADD, type_=ofproto.OFPGT_ALL, group_id=group_id, buckets=buckets) #GroupMod
                switch.send_msg(req) #controller sends GroupMod to current OVS switch
                self.__broadcast_rules[dpid].append(group_id) #memorize group ID for current core switch

                match=ofp_parser.OFPMatch(eth_type=0x0800, in_port=i, ipv4_dst=self.__broadcastAddress) #matching for broadcast traffic
                actions=[ofp_parser.OFPActionGroup(group_id)] #action for OVS switch: forward out of all ports specified in the group
                self.add_flow(datapath=switch, match=match, actions=actions, priority=6, hard_timeout=200) #install flow rule for broadcast traffic on current sw

    '''Computes reactively routing paths for detected elephant flows according to current congestion level topology's links. Elephant flow rules are 
       matched on the 5-tuple <source IPv4, destination Ipv4, L4 protocol, L4 source port number, L4 destination port number>. Ad-hoc elephant flow rules
       are highly specific for a fat-tree topology:
            1) If source and destination servers are connected to the same edge switch, a single flow rule is installed in that edge switch, simply forwarding 
               packets from the input port to the correct output port;
            2) If source and destination servers are located in the same herd, but connected to different edge switches, the first edge switch (connected to 
               source server) will distribute the flow out of all its currently active up ports. Distribution is achieved through a SELECT group rule installed 
               in the switch group table. The behavior of a group SELECT it to execute only one bucket (forward out of a single upward port), according to a 
               given probability weight: buckets with the highest weight also have the highest probability to be selected for the current matching packet. 
               The weight of each bucket in the SELECT group will reflect the current level of congestion of the corresponding link: the effect is to distribute 
               the elephant flow on multiple upward paths according to the current network load (less congested link gets more packets, more congested links get 
               less packets). Having reached the aggregation level, traffic will proceed downward through a single path (agg → edge, edge → server) from each 
               aggregation switch to the destination;
            3) If source and destination servers are located in different herds, the first edge switch (connected to source server) will distribute the flow out 
               of all its currently-active up ports (just as described in point 2). Then, all reached aggregation switches will repeat the process, distributing 
               the flow out all their active up ports (towards core switches). Having reached the core level, separated traffic will proceed downward through a 
               single path (core → agg, agg → edge, edge → server) from each core switch to the destination;
       Elephant flow rules are installed on OVS switches with priority value of 200 (higher than default static ECMP rules) and a 60 [s] idle timeout (if the 
       rule is not matched for a minute, the flow is assumed to be finished and the rule is removed from the flow table).
       @param ECMP13 object
       @param MsgBase message (Packet-In message)
       @param str src_ipv4
       @param str dst_ipv4
       @param int l4_protocol
       @param str l4_protocol_name
       @param int src_port
       @param int dst_port'''
    def route_elephant_flows(self, message, src_ipv4, dst_ipv4, l4_protocol, l4_protocol_name, src_port, dst_port):
        src=[s for s in self.__topo.get_layer_nodes(FatTree.server_layer()) if self.__topo.get_ipv4(name=s)==src_ipv4][0] #source server's name
        dst=[s for s in self.__topo.get_layer_nodes(FatTree.server_layer()) if self.__topo.get_ipv4(name=s)==dst_ipv4][0] #destination server's name
        with open(log_path, "a") as log_file:
            log_file.write(f"{dt.now()} -> Detected {l4_protocol_name} elephant flow between {src} ({src_ipv4}:{src_port}) and {dst} ({dst_ipv4}:{dst_port}). "
                           f"Installing ad-hoc flow rules\n")
            log_file.write(f"\n")

        if not self.graph.has_node(self.__topo.get_mac(name=src)) or not self.graph.has_node(self.__topo.get_mac(name=dst)): #servers disconnected
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Communicating servers {src} and {dst} seems to be not correctly registered at controller's site\n")
                log_file.write(f"\n")
            return #abort computation

        src_mac=self.__topo.get_mac(name=src) #MAC address of source server
        dst_mac=self.__topo.get_mac(name=dst) #MAC address of destination server

        edge_src=self.__topo.get_up_nodes(src)[0] #get edge switch serving source server
        edge_src_dpid=ECMP13.int_dpid(self.__topo.get_dpid(name=edge_src)) #get DPID (integer) identifying first edge switch (serving src server)
        if not self.graph.has_edge(src_mac, edge_src_dpid): #if source server, despite being active, has no connection to an edge switch
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> No starting link. {src} is isolated and cannot communicate in the network\n")
                log_file.write(f"\n")
            return #abort computation
        try:
            e_sw_src=self.__datapaths[edge_src_dpid] #datapath reference of first edge OVS switch (connected to source)
            ofproto_start=e_sw_src.ofproto #OpenFlow 1.3
            ofp_parser_start=e_sw_src.ofproto_parser #to manage OpenFlow messages
        except KeyError: #if edge_src_dpid is not a key in the dictionary __datapaths
            print(f'Specified DPID {edge_src_dpid} does not correspond to any switch in the topology')
            return #abort computation
        except AttributeError: #if e_sw_src is None
            print(f'Switch {edge_src} ({edge_src_dpid}) is not currently active or seems not properly registered')
            return #abort computation

        edge_dst=self.__topo.get_up_nodes(dst)[0] #get edge switch serving dst server
        edge_dst_dpid=ECMP13.int_dpid(self.__topo.get_dpid(name=edge_dst)) #get DPID (integer) identifying last edge switch (serving dst server)
        if not self.graph.has_edge(dst_mac, edge_dst_dpid): #if destination server, despite being active, has no connection to an edge switch
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Routing {src} -> {dst}. {dst} is isolated and cannot be reached from {src}\n")
                log_file.write(f"\n")
            return #abort computation
        try:
            e_sw_dst=self.__datapaths[edge_dst_dpid] #datapath reference to last edge OVS switch (connected to destination)
            ofp_parser_end=e_sw_dst.ofproto_parser #to create OpenFlow messages
        except KeyError: #if edge_dst_dpid is not a key in the dictionary __datapaths
            print(f'Specified DPID {edge_dst_dpid} does not correspond to any switch in the topology')
            return #abort computation
        except AttributeError: #if e_sw_dst is None
            print(f'Switch {edge_dst} ({edge_dst_dpid}) is not currently active or seems not properly registered')
            return #abort computation

        if edge_src==edge_dst: #if source and destination server are connected to the same edge switch
            in_port=self.__topo.port(src, edge_src)[1] #ingress port on edge switch from source server
            out_port=self.__topo.port(edge_src, dst)[0] #egress port on edge switch towards destination server
            actions=[ofp_parser_start.OFPActionOutput(out_port)] #action: output message out of port towards destination server
            if l4_protocol==inet.IPPROTO_TCP: #match IPv4 - TCP elephant flow
                match=ofp_parser_start.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                ip_proto=l4_protocol, tcp_src=src_port, tcp_dst=dst_port)
            else: #match IPv4 - UDP elephant flow
                match=ofp_parser_start.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                  ip_proto=l4_protocol, udp_src=src_port, udp_dst=dst_port)
            self.add_flow(datapath=e_sw_src, match=match, actions=actions, priority=200, idle_timeout=60) #install ad-hoc flow rule at current edge switch
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Flow rules installed for elephant flow between {src} and {dst}\n")
                log_file.write(f"{dt.now()} -> sw={edge_src}, in port={in_port}, out port={out_port}\n")
                log_file.write(f"\n")

            #handle marked message (notification of discovered elephant) with flow mod (only at first edge switch)
            data=None #content of packet out message
            if message.buffer_id==ofproto_start.OFP_NO_BUFFER: #if no buffer ID was specified in the Packet-In message
                data=message.data #append to packet out the notification packet that has triggered packet in
            out=ofp_parser_start.OFPPacketOut(datapath=e_sw_src, buffer_id=message.buffer_id, in_port=in_port, actions=actions, data=data) #packet out message
            e_sw_src.send_msg(out) #controller send packet out to OVS switch

        elif self.__topo.get_herd_id(src)==self.__topo.get_herd_id(dst): #if source and destination reside in the same herd (but connect on different edge switches)
            in_port=self.__topo.port(src, edge_src)[1] #ingress port on first edge switch from source server
            hash_data=f"{src_ipv4},{dst_ipv4},{l4_protocol},{src_port},{dst_port}" #compute group ID based on flow 5-tuple using hashing
            hashed=hashlib.sha256(hash_data.encode()).hexdigest() #compute SHA-256 hashing
            group_id=int(hashed, 16)%(2**32) #ensure group ID is a 32-bit unsigned integer

            if group_id in self.__elephant_rules[edge_src_dpid]: #clean previous elephant group rule from first edge switch group table
                del_req=ofp_parser_start.OFPGroupMod(datapath=e_sw_src, command=ofproto_start.OFPGC_DELETE, group_id=group_id)
                e_sw_src.send_msg(del_req) #controller sends GroupMod to first edge OVS switch to clear previous entry for this group
                self.__elephant_rules[edge_src_dpid].remove(group_id) #remove memorized group ID for the first edge switch

            #list of all aggregation switches connected to the first edge switch
            aggs=[a for a in self.__topo.get_up_nodes(edge_src) if self.graph.has_edge(edge_src_dpid, ECMP13.int_dpid(self.__topo.get_dpid(name=a)))]
            if len(aggs)==0: #if first edge switch (connected to source) has no connection currently active toward an aggregation switch
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> No connection active on switch {edge_src}. No path between {src} and {dst}.\n")
                    log_file.write(f"\n")
                return #abort computation

            ports=[] #list of exit ports for first edge switch (distribute to aggregation switches)
            buckets=[] #initialize list of buckets for the group (each bucket has 1 action: forward out of an exit port)

            #how to compute bucket weights for flows distribution according to current traffic load
            weights=[] #initialize weights for buckets in the group
            loads=[] #congestion of links "first edge switch - aggregation switch"
            for link in self.__topo.get_up_edges(edge_src): #for all upward links of the first edge switch
                if self.graph.has_edge(edge_src_dpid, ECMP13.int_dpid(self.__topo.get_dpid(name=link[1]))):
                    link_name=f"{link[0]}-{link[1]}" #get link name
                    loads.append(self.__link_df.loc[self.__link_df['link_name']==link_name, 'congestion'].iloc[0]) #get link congestion rate from dataframe

            inverse_loads=[1-load for load in loads]
            for i in range(len(aggs)): #for each aggregation switch currently reachable from the fist edge switch
                if i==len(aggs)-1:
                    weights.append(100-sum(weights)) #weight assigned in the group to the port towards the last agg switch
                else:
                    inverse_load=1-loads[i]
                    weights.append(int((inverse_load/sum(inverse_loads))*100)) #weight assigned in the group to the port towards the i-th agg switch

            for i, a in enumerate(aggs): #for each aggregation switch currently reachable from the fist edge switch
                weight=weights[i] #weigth assigned to bucket i
                ports.append((a, self.__topo.port(edge_src, a)[0])) #ports towards current agg switch
                action=ofp_parser_start.OFPActionOutput(self.__topo.port(edge_src, a)[0]) #action forward out of port from first edge sw to current agg sw
                buckets.append(ofp_parser_start.OFPBucket(weight=weight, actions=[action]))
            req=ofp_parser_start.OFPGroupMod(datapath=e_sw_src, command=ofproto_start.OFPFC_ADD, type_=ofproto_start.OFPGT_SELECT,
                                             group_id=group_id, buckets=buckets) #SELECT group rule for elephant flow
            e_sw_src.send_msg(req) #controller sends GroupMod to first edge OVS switch to install group rule
            self.__elephant_rules[edge_src_dpid].append(group_id) #add memorized group ID for first edge switch

            actions=[ofp_parser_start.OFPActionGroup(group_id)] #action for first edge OVS switch: distribute flow packets among ports specified in the group
            if l4_protocol==inet.IPPROTO_TCP: #match IPv4 - TCP elephant flow
                match=ofp_parser_start.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                ip_proto=l4_protocol, tcp_src=src_port, tcp_dst=dst_port)
            else: #match IPv4 - UDP elephant flow
                match=ofp_parser_start.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                ip_proto=l4_protocol, udp_src=src_port, udp_dst=dst_port)
            self.add_flow(datapath=e_sw_src, match=match, actions=actions, priority=200, idle_timeout=60) #install flow rule on first edge switch
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Routing elephant flow between {src} and {dst}\n")
                log_file.write(f"{dt.now()} -> sw={edge_src}, in port={in_port}, out ports={ports}, weights={weights} (group={group_id})\n")

            #handle marked message (notification of discovered elephant flow) with flow mod (only at first edge switch)
            data=None #content of packet out message
            if message.buffer_id==ofproto_start.OFP_NO_BUFFER: #if no buffer ID was specified in the packet in message
                data=message.data #append to packet out the flag packet that has triggered packet in
            out=ofp_parser_start.OFPPacketOut(datapath=e_sw_src, buffer_id=message.buffer_id, in_port=in_port, actions=actions, data=data) #packet out message

            count=len(aggs) #counter of agg switches in the herd. Decremented when an agg switch is not connected to edge switch serving destination
            for a in aggs: #for all agg switches reachable from first edge switch
                a_dpid=ECMP13.int_dpid(self.__topo.get_dpid(name=a)) #DPID of current agg OVS switch
                assert a_dpid in self.__datapaths.keys(), f'Specified DPID {a_dpid} does not correspond to any switch in the topology'
                a_switch=self.__datapaths[a_dpid] #datapath reference to current agg OVS switch
                assert a_switch is not None, f'Switch {a} (DPID={a_dpid}) seems to be disconnected or not correctly registered'
                ofp_parser_a=a_switch.ofproto_parser #to create OpenFlow messages
                if not self.graph.has_edge(a_dpid, edge_dst_dpid): #if current agg switch is not connected towards last edge switch
                    count-=1 #decrement counter
                    if count==0: #if counter reaches zero, this means that edge switch serving destination is isolated (not reachable)
                        with open(log_path, "a") as log_file:
                            log_file.write(f"{dt.now()} -> Switch {edge_dst} isolated. No path available between {src} and {dst}\n")
                            log_file.write(f"\n")
                        return #abort computation
                    else:
                        with open(log_path, "a") as log_file:
                            log_file.write(f"{dt.now()} -> Routing {src} -> {dst}. No connection from switch {a} to switch {edge_src}\n")
                            log_file.write(f"\n")
                        continue #try next agg

                in_port=self.__topo.port(edge_src, a)[1] #ingress port from first edge switch into current agg switch
                out_port=self.__topo.port(a, edge_dst)[0] #egress port on current agg switch towards last edge switch (connected to destination)
                actions=[ofp_parser_a.OFPActionOutput(out_port)] #output message out of port towards last edge switch
                if l4_protocol==inet.IPPROTO_TCP: #match IPv4 - TCP elephant flow
                    match=ofp_parser_a.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                ip_proto=l4_protocol, tcp_src=src_port, tcp_dst=dst_port)
                else: #match IPv4 - UDP elephant flow
                    match=ofp_parser_a.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                ip_proto=l4_protocol, udp_src=src_port, udp_dst=dst_port)
                self.add_flow(datapath=a_switch, match=match, actions=actions, priority=200, idle_timeout=60) #install flow rule on current agg switch
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> sw={a}, in port={in_port}, out port={out_port}\n")

                in_port=self.__topo.port(a, edge_dst)[1] #ingress port on last edge switch from current aggregation switch
                out_port=self.__topo.port(edge_dst, dst)[0] #egress port on last edge switch towards destination server
                actions=[ofp_parser_end.OFPActionOutput(out_port)] #action: output message out of port towards destination
                if l4_protocol==inet.IPPROTO_TCP: #match IPv4 - TCP elephant flow
                    match=ofp_parser_end.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                  ip_proto=l4_protocol, tcp_src=src_port, tcp_dst=dst_port)
                else: #match IPv4 - UDP elephant flow
                    match=ofp_parser_end.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                    ip_proto=l4_protocol, udp_src=src_port, udp_dst=dst_port)
                self.add_flow(datapath=e_sw_dst, match=match, actions=actions, priority=200, idle_timeout=60) #install flow rule on last edge switch
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> sw={edge_dst}, in port={in_port}, out port={out_port}\n")

                e_sw_src.send_msg(out) #controller sends packet out message to switch

            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Flow rules installed for elephant flow between {src} and {dst}\n")
                log_file.write(f"\n")

        else: #src and dst do not reside in the same herd
            in_port=self.__topo.port(src, edge_src)[1] #ingress port on first edge switch from source server
            hash_data=f"{src_ipv4},{dst_ipv4},{l4_protocol},{src_port},{dst_port}" #compute group ID based on flow 5-tuple using hashing
            hashed=hashlib.sha256(hash_data.encode()).hexdigest() #compute SHA-256 hashing
            group_id=int(hashed, 16)%(2**32) #ensure group ID is a 32-bit unsigned integer

            #Clear previous group-rule for elephant flow in the group table of first edge switch
            if group_id in self.__elephant_rules[edge_src_dpid]:
                del_req=ofp_parser_start.OFPGroupMod(datapath=e_sw_src, command=ofproto_start.OFPGC_DELETE, group_id=group_id)
                e_sw_src.send_msg(del_req) #controller sends GroupMod to first edge OVS switch to clear previous entry for this group
                self.__elephant_rules[edge_src_dpid].remove(group_id) #remove memorized group ID for first edge switch

            #list of aggregation switches reachable from first edge switch
            aggs=[a for a in self.__topo.get_up_nodes(edge_src) if self.graph.has_edge(edge_src_dpid, ECMP13.int_dpid(self.__topo.get_dpid(name=a)))]
            if len(aggs)==0: #if first edge switch (connected to source) has no connection currently active toward an aggregation switch
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Routing {src} -> {dst}. No upward connection active on switch {edge_src}\n")
                    log_file.write(f"\n")
                return #abort computation

            ports=[] #list of active upward ports of first edge switch
            buckets=[] #initialize list of buckets for the group (each bucket has 1 action: forward out of one of the upward exit ports)

            #compute bucket weights for flows distribution according to current traffic load
            weights=[] #initialize weights for buckets in the group
            loads=[] #congestion rate of upward links of first edge switch
            for link in self.__topo.get_up_edges(edge_src): #for each upward link of first edge switch
                if self.graph.has_edge(edge_src_dpid, ECMP13.int_dpid(self.__topo.get_dpid(name=link[1]))): #if the link is currently active
                    link_name=f"{link[0]}-{link[1]}" #link name
                    loads.append(self.__link_df.loc[self.__link_df['link_name']==link_name, 'congestion'].iloc[0]) #fecth link congestion rate from dataframe

            inverse_loads=[1-load for load in loads]
            for i in range(len(aggs)): #for each aggregation switch currently reachable from the fist edge switch
                if i==len(aggs)-1:
                    weights.append(100-sum(weights)) #weight assigned in the group to the port towards the last agg switch
                else:
                    inverse_load=1-loads[i]
                    weights.append(int((inverse_load /sum(inverse_loads))*100)) #weight assigned in the group to the port towards the i-th agg switch

            for i, a in enumerate(aggs): #for each aggregation switch currently reachable from the fist edge switch
                weight=weights[i] #weigth assigned to bucket i
                ports.append((a, self.__topo.port(edge_src, a)[0])) #outport towards i-th reachable aggregation switch
                action=ofp_parser_start.OFPActionOutput(self.__topo.port(edge_src, a)[0]) #action: forward out of port from first edge sw to current agg sw
                buckets.append(ofp_parser_start.OFPBucket(weight=weight, actions=[action]))

            req=ofp_parser_start.OFPGroupMod(datapath=e_sw_src, command=ofproto_start.OFPFC_ADD, type_=ofproto_start.OFPGT_SELECT,
                                             group_id=group_id, buckets=buckets) #group mod message for elephant flow
            e_sw_src.send_msg(req) #controller sends GroupMod to first edge OVS switch to install group rule
            self.__elephant_rules[edge_src_dpid].append(group_id) #memorize group ID for group rule for first edge switch

            actions=[ofp_parser_start.OFPActionGroup(group_id)] #action for first edge switch: distribute the flow among all ports specified in the group
            if l4_protocol==inet.IPPROTO_TCP: #match IPv4 - TCP elephant flow
                match=ofp_parser_start.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                ip_proto=l4_protocol, tcp_src=src_port, tcp_dst=dst_port)
            else: #match IPv4 - UDP elephant flow
                match=ofp_parser_start.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                ip_proto=l4_protocol, udp_src=src_port, udp_dst=dst_port)
            self.add_flow(datapath=e_sw_src, match=match, actions=actions, priority=200, idle_timeout=60) #install flow rule on first edge switch
            with open(log_path, "a") as log_file:
                log_file.write(f"{dt.now()} -> Routing elephant flow between {src} and {dst}\n")
                log_file.write(f"{dt.now()} -> sw={edge_src}, in port={in_port}, out ports={ports}, weights={weights} (group={group_id})\n")

            #handle marked message (elephant flow notification) with flow mod (only at first edge switch)
            data=None #content of packet out message
            if message.buffer_id==ofproto_start.OFP_NO_BUFFER: #if no buffer ID was specified in the packet in message
                data=message.data #append to packet out the flag packet that has triggered the packet in
            out=ofp_parser_start.OFPPacketOut(datapath=e_sw_src, buffer_id=message.buffer_id, in_port=in_port, actions=actions, data=data) #packet out message

            count1=len(aggs) #counter of agg sw connected to first edge sw. Decremented each time it is not possible to reach destination from an agg switch
            for a in aggs: #for all agg switches reachable from first edge switch
                a_dpid=ECMP13.int_dpid(self.__topo.get_dpid(name=a)) #DPID of current agg OVS switch
                assert a_dpid in self.__datapaths.keys(), f'Specified DPID {a_dpid} does not correspond to any switch in the topology'
                a_switch=self.__datapaths[a_dpid] #datapath reference to current agg OVS switch
                assert a_switch is not None, f'Switch {a} (DPID={a_dpid}) seems to be disconnected or not correctly registered'
                ofproto_a=a_switch.ofproto #OpenFlow 1.3
                ofp_parser_a=a_switch.ofproto_parser #to create OpenFlow messages

                #clear previous group-rule for elephant flow from group table of current agg switch
                if len(self.__elephant_rules[a_dpid])>0 and group_id in self.__elephant_rules[a_dpid]:
                    del_req=ofp_parser_a.OFPGroupMod(datapath=a_switch, command=ofproto_a.OFPGC_DELETE, group_id=group_id)
                    a_switch.send_msg(del_req) #controller sends GroupMod to current agg OVS switch to clear previous entry for this group
                    self.__elephant_rules[a_dpid].remove(group_id) #remove memorized group ID for current agg switch

                #list of core switches currently reachable from the current agg switch
                cores=[c for c in self.__topo.get_up_nodes(a) if self.graph.has_edge(a_dpid, ECMP13.int_dpid(self.__topo.get_dpid(name=c)))]
                if len(cores)==0: #if current agg switch has no connection currently active toward a core switch
                    count1-=1 #decrement counter
                    if count1==0: #if count1 reaches zero, this means that from all agg switches is not possible to reach core layer
                        break #no path is available, exit loop on aggregation switches
                    else:
                        with open(log_path, "a") as log_file:
                            log_file.write(f"{dt.now()} -> Routing {src} -> {dst}. No connection from switch {a} to core layer switches\n")
                            log_file.write(f"\n")
                        continue #try next agg

                ports2=[] #list of exit ports on current agg switch towards core switches
                buckets=[] #initialize list of buckets for the group

                #how to compute bucket weights for flows distribution according to current traffic load
                weights2=[] #initialize weights for buckets in the group
                loads2=[] #congestion rate of upward links (towards core switches) of current agg switch
                for link in self.__topo.get_up_edges(a): #for each upward link of current agg switch
                    if self.graph.has_edge(ECMP13.int_dpid(self.__topo.get_dpid(name=a)), ECMP13.int_dpid(self.__topo.get_dpid(name=link[1]))):
                        link_name=f"{link[0]}-{link[1]}" #fetch link name
                        loads2.append(self.__link_df.loc[self.__link_df['link_name'] == link_name, 'congestion'].iloc[0]) #fetch link congestion rate from df

                inverse_loads2=[1-load for load in loads2]
                for i in range(len(cores)): #for each core switch currently reachable from the current agg switch
                    if i==len(cores)-1:
                        weights2.append(100 -sum(weights2)) #weight assigned in the group to the port towards the last core switch
                    else:
                        inverse_load=1-loads2[i]
                        weights2.append(int((inverse_load/sum(inverse_loads2))*100)) #weight assigned in the group to the port towards the i-th core switch

                for i, c in enumerate(cores): #for each core switch currently reachable from current agg switch
                    weight=weights2[i] #weigth assigned to bucket i
                    ports2.append((c, self.__topo.port(a, c)[0])) #port towards current core switch
                    action=ofp_parser_a.OFPActionOutput(self.__topo.port(a, c)[0]) #action: forward out of port from current agg switch to core switch
                    buckets.append(ofp_parser_a.OFPBucket(weight=weight, actions=[action]))
                req=ofp_parser_a.OFPGroupMod(datapath=a_switch, command=ofproto_a.OFPFC_ADD, type_=ofproto_a.OFPGT_SELECT, group_id=group_id, buckets=buckets)
                a_switch.send_msg(req) #controller sends GroupMod to current agg OVS switch to install group rule
                self.__elephant_rules[a_dpid].append(group_id) #memorize group rule for current agg switch

                in_port=self.__topo.port(edge_src, a)[1] #ingress port from first edge switch into current agg switch
                actions=[ofp_parser_a.OFPActionGroup(group_id)] #action for current agg OVS switch: distribute flow out of all ports specified in the group
                if l4_protocol==inet.IPPROTO_TCP: #match IPv4 - TCP elephant flow
                    match=ofp_parser_a.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                ip_proto=l4_protocol, tcp_src=src_port, tcp_dst=dst_port)
                else: #match IPv4 - UDP elephant flow
                    match=ofp_parser_a.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                ip_proto=l4_protocol, udp_src=src_port, udp_dst=dst_port)
                self.add_flow(datapath=a_switch, match=match, actions=actions, priority=200, idle_timeout=60) #install flow rule on current agg switch
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> sw={a}, in port={in_port}, out ports={ports2}, weights={weights2} (group={group_id})\n")

                count2=len(cores) #counter of core sw connected to current agg sw. Decremented each time it is not possible to reach destination from core
                for c in cores: #for all core switches reachable from current agg switch
                    c_dpid=ECMP13.int_dpid(self.__topo.get_dpid(name=c)) #DPID of current core OVS switch
                    assert c_dpid in self.__datapaths.keys(), f'Specified DPID {c_dpid} does not correspond to any switch in the topology'
                    c_switch=self.__datapaths[c_dpid] #datapath reference to current core OVS switch
                    assert c_switch is not None, f'Switch {c} (DPID={c_dpid}) seems to be disconnected or not correctly registered'
                    ofp_parser_c=c_switch.ofproto_parser #to create OpenFlow messages

                    #get aggregation switch in the herd of destination server connected to current core switch (last agg switch)
                    last_agg=[a2 for a2 in self.__topo.get_down_nodes(c) if self.__topo.get_herd_id(a2)==self.__topo.get_herd_id(dst)][0]
                    if not self.graph.has_edge(c_dpid, ECMP13.int_dpid(self.__topo.get_dpid(name=last_agg))):
                        count2-=1 #decrement counter
                        if count2==0: #if count2 reaches zero, this means that from none of the core switches it is possible to reach destination
                            break #no path is available, exit loop on core switches
                        else:
                            with open(log_path, "a") as log_file:
                                log_file.write(f"{dt.now()} -> Routing {src} -> {dst}. No connection from sw {c} towards sw {last_agg}\n")
                                log_file.write(f"\n")
                            continue #try next core switch

                    in_port=self.__topo.port(a, c)[1] #ingress port from current agg switch into current core switch
                    out_port=self.__topo.port(c, last_agg)[0] #egress port on current core switch towards last agg switch (connected to last edge switch)
                    actions=[ofp_parser_c.OFPActionOutput(out_port)] #output message out of port towards last agg switch
                    if l4_protocol==inet.IPPROTO_TCP: #match IPv4 - TCP elephant flow
                        match=ofp_parser_c.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                    ip_proto=l4_protocol, tcp_src=src_port, tcp_dst=dst_port)
                    else: #match IPv4 - UDP elephant flow
                        match=ofp_parser_c.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                      ip_proto=l4_protocol, udp_src=src_port, udp_dst=dst_port)
                    self.add_flow(datapath=c_switch, match=match, actions=actions, priority=200, idle_timeout=60) #install flow rule on current core switch
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> sw={c}, in port={in_port}, out port={out_port}\n")

                    last_agg_dpid=ECMP13.int_dpid(self.__topo.get_dpid(name=last_agg)) #DPID of last agg OVS switch on path
                    assert last_agg_dpid in self.__datapaths.keys(), f'Specified DPID {last_agg_dpid} does not correspond to any switch in the topology'
                    agg_switch=self.__datapaths[last_agg_dpid] #datapath reference to last agg OVS switch on path
                    assert agg_switch is not None, f'Switch {last_agg} (DPID={last_agg_dpid}) seems to be disconnected or not correctly registered'
                    ofp_parser_agg=agg_switch.ofproto_parser #to create OpenFlow messages
                    if not self.graph.has_edge(last_agg_dpid, edge_dst_dpid): #check connection between last agg switch and last edge switch in the path
                        count2-=1 #decrement counter
                        if count2==0: #if count2 reaches zero, this means that from none of the core switches it is possible to reach destination
                            break #no path is available, exit loop on core switches
                        else:
                            with open(log_path, "a") as log_file:
                                log_file.write(f"{dt.now()} -> Routing {src} -> {dst}. No connection from sw {last_agg} to sw {edge_dst}\n")
                                log_file.write(f"\n")
                            continue #go to next core

                    in_port=self.__topo.port(c, last_agg)[1] #ingress port from current core switch to last agg switch
                    out_port=self.__topo.port(last_agg, edge_dst)[0] #egress port on last agg switch towards last edge switch (connected to destination)
                    actions=[ofp_parser_agg.OFPActionOutput(out_port)] #output message out of port towards last edge switch
                    if l4_protocol==inet.IPPROTO_TCP: #match IPv4 - TCP elephant flow
                        match=ofp_parser_agg.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                      ip_proto=l4_protocol, tcp_src=src_port, tcp_dst=dst_port)
                    else: #match IPv4 - UDP elephant flow
                        match=ofp_parser_agg.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                        ip_proto=l4_protocol, udp_src=src_port, udp_dst=dst_port)
                    self.add_flow(datapath=agg_switch, match=match, actions=actions, priority=200, idle_timeout=60) #install flow rule on last agg switch
                    with open(log_path, "a") as log_file:
                         log_file.write(f"{dt.now()} -> sw={last_agg}, in port={in_port}, out port={out_port}\n")

                    in_port=self.__topo.port(last_agg, edge_dst)[1] #ingress port on last edge switch from last aggregation switch
                    out_port=self.__topo.port(edge_dst, dst)[0] #egress port on last edge switch towards destination server
                    actions=[ofp_parser_end.OFPActionOutput(out_port)] #action: output message out of port towards destination
                    if l4_protocol==inet.IPPROTO_TCP: #match IPv4 - TCP elephant flow
                        match=ofp_parser_end.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                      ip_proto=l4_protocol, tcp_src=src_port, tcp_dst=dst_port)
                    else: #match IPv4 - UDP elephant flow
                        match=ofp_parser_end.OFPMatch(eth_type=0x0800, in_port=in_port, ipv4_src=src_ipv4, ipv4_dst=dst_ipv4,
                                                      ip_proto=l4_protocol, udp_src=src_port, udp_dst=dst_port)
                    self.add_flow(datapath=e_sw_dst, match=match, actions=actions, priority=200, idle_timeout=60) #install flow rule on last edge switch
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> sw={edge_dst}, in port={in_port}, out port={out_port}\n")
                        log_file.write(f"\n")

                if count2==0: #if destination server could not be reached from current agg switch
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> Routing {src} -> {dst}. Destination unreachable from {a}\n")
                        log_file.write(f"\n")
                    count1-=1 #decrement other counter
            if count1==0: #if destination server could not be reached from first edge switch
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> No path available between {src} and {dst}\n")
                    log_file.write(f"\n")
                return #abort computation
            else: #if destination server was reached
                e_sw_src.send_msg(out) #controller sends packet out message to switch to handle flag packet

                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Flow rules installed for elephant flow between {src} and {dst}\n")
                    log_file.write(f"\n")

    ###################################################################################################Utility Functions
    '''Install flow rule in the flow table of current OVS switch (the controller sends a FlowMod message to the current switch)
       @param ECMP13 object
       @param Datapath datapath (reference to current switch)
       @param OFPMatch match
       @param OFPAction actions
       @param int priority (default 0)
       @param int idle_timeout (default 0, meaning no idle timeout)
       @param int hard_timeout (default 0, meaning no hard timeout)
       @param int buffer_id (default None, meaning no buffer ID)'''
    def add_flow(self, datapath, match, actions, priority=0, idle_timeout=0, hard_timeout=0, buffer_id=None):
        if not self.__firstConnection: #skip when installing table-miss rule or marked packets rule (during boot-up, dictionary __datapaths is not populated)
            switch_name=self.__topo.get_name(dpid=datapath.id) #get name of current switch
            assert datapath.id in self.__datapaths.keys(), f'Specified instance {datapath}({datapath.id} does not refer to any switch connected to controller)'
            assert switch_name in self.__topo.switches(), f'Specified instance {datapath}({datapath.id} does not refer to any switch connected to controller)'
        ofproto=datapath.ofproto #to handle OpenFlow protocol 1.3
        parser=datapath.ofproto_parser #to create and manage OpenFlow messages
        inst=[parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)] #specify to OVS switch instructions to apply actions
        if buffer_id: #if a valid buffer ID has been specified by OVS switch to controller
            mod=parser.OFPFlowMod(datapath=datapath, match=match, priority=priority, idle_timeout=idle_timeout, hard_timeout=hard_timeout,
                                    buffer_id=buffer_id, instructions=inst, command=ofproto.OFPFC_ADD) #create FlowMod message
        else: #if NO valid buffer ID has been specified
            mod=parser.OFPFlowMod(datapath=datapath, match=match, priority=priority, idle_timeout=idle_timeout, hard_timeout=hard_timeout,
                                    instructions=inst, command=ofproto.OFPFC_ADD) #create FlowMod message
        datapath.send_msg(mod) #send FlowMod message to OVS switch to install new flow rule

    '''Saves current link's stat (pandas dataframe format) into a .csv file. If the file does not exist, it creates one
       @param pd.DataFrame df (data to append)
       @param str file_name'''
    @staticmethod
    def export_stats(df, file_name):
        file_path=os.path.join(stat_folder, file_name)
        file_exists=os.path.isfile(file_path) #checks if the file exists
        df.to_csv(file_path, mode='a', index=False, header=not file_exists) #append to file if it exists, otherwise create a new file

    '''Given a DPID expressed as hexadecimal string (how Mininet library handles DPIDs), it returns its value as integer (how Ryu library handles DPIDs)
       @param str hex_string
       @return int value'''
    @staticmethod
    def int_dpid(hex_string):
        return int(hex_string, 16)

    '''Return value of instance attribute __link_df (pandas dataframe containing up-to-date link stats)
       @param ECMP13 self
       @return DataFrame link_df'''
    @property
    def link_df(self):
        return self.__link_df

#################################################################################################### REST API Web Server
class RestController(ControllerBase): #inherit from ControllerBase class

    """Creates instance of RestController"""
    def __init__(self, req, link, data, **config):
        super(RestController, self).__init__(req, link, data, **config) #calls constructor of super class
        self.rest_api_controller=data[REST_API_INSTANCE_NAME] #initialize name of ECMP13 instance

    '''Return standardized error response to HTTP request in JSON format
       @param str message
       @param in status (default=400)
       @return wsgi.Response response'''
    @staticmethod
    def error_response(message, status=400):
        return Response(content_type='application/json', body=json.dumps({"error": message}), status=status)

    '''Convert a Pandas DataFrame object from into a list of dictionaries
       @param DataFrame df
       @return <str: str>[] dataframe to dictionary'''
    @staticmethod
    def dataframe_to_dict(df):
        if not df.empty: #checks if the dataframe is not empty
            for column in df.select_dtypes(include=['datetime64[ns]', 'datetimetz']).columns: #converts values datetime columns into strings
                df[column]=df[column].astype(str)
            for column in df.select_dtypes(include=['object']).columns: #converts object values in columns into strings
                df[column]=df[column].astype(str)
        return df.to_dict(orient='records') #return the converted dataframe

    '''Having received an HTTP GET request, return up-to-date link stats from the controller
       @param RestController object
       @return wsgi.Response response'''
    @route('congestiondata', '/congestiondata', methods=['GET']) #exposed REST API endpoint for HTTP GET request
    def get_link_data(self):
        controller=self.rest_api_controller #get ECMP13 instance
        df=controller.link_df #access link stats dataframe from ECMP13 instance
        df_2=df.copy(deep=True) #create deep copy of the dataframe to preserver ECMP13 instance's attribute
        data=self.dataframe_to_dict(df_2) #converts dataframe in JSON format to be exposed through REST API
        return Response(content_type='application/json', body=json.dumps(data), status=200)
