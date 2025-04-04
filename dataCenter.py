#!/usr/bin/python3

"""This script uses Mininet to emulate a data center network and run traffic simulations on it
Running command:
sudo python3 dataCenter.py -k=[int] --core-agg-bw=[float] --core-agg-loss=[int] --core-agg-delay=[str] --core-agg-jitter=[str] --core-agg-max-queue=[int]
                           --agg-edge-bw=[float] --agg-edge-loss=[int] --agg-edge-delay=[str] --agg-edge-jitter=[str] --agg-edge-max-queue=[int]
                           --edge-server-bw=[float] --edge-server-loss=[int] --edge-server-delay=[str] --edge-server-jitter=[str] --edge-server-max-queue=[int]
                           --arp (optional)
Default values are provided if topology parameters are not specified"""

from mininet.net import Mininet #emulate the network
from mininet.node import RemoteController, OVSKernelSwitch #specify type of controller and switch devices
from mininet.link import TCLink #define Ethernet interfaces
from mininet.cli import CLI #start/stop Mininet's command line
from mininet.log import setLogLevel #regulate verbosity of Mininet's output

from fatTreeTopo import FatTree #custom class, define data center topology

import argparse #parsing CLI arguments
import sys #interaction with runtime environment
import os #interaction with OS
import threading #running threads
from filelock import FileLock #ensure thread-safe access to a file

import pandas as pd #manipulating data in DataFrame and Series objects
import time #time-related functions
from datetime import datetime as dt #date-related functions
import random #generate pseudo-random extractions
import math #mathematical operations
import numpy as np #optimized mathematical operations on multidimensional arrays
from scipy.optimize import fsolve #sole non-linear equations

import requests #send HTTP requests

################################################################################################Energy-Aware Application
active_switches={} #dictionary <switch_name: True/False> (if value is True, switch is active, otherwise is inactive)
deactivation_count={} #dictionary <switch_name: int> (if 0 switch can be deactivated, if >0 switch cannot be deactivated)
turn_off_probability={} #dictionary <switch_name: float> (assign to each switch a probability value in [0,1] to be turned off)
url="http://localhost:8080/congestiondata" #REST API endpoint (where Ryu controller exposes current link stats)
log_path="./LogFiles/energyControlLoop.txt" #text file where application records logs of all performed operations

base_interval=15 #base value used to dynamically update monitoring interval
min_interval=180 #minimum monitoring interval
max_interval=240 #maximum monitoring interval

'''Thread target function. Periodically, it fetches current link stats from Ryu controller (which exposes data through a REST API). According to link status,
   it decides whether to turn off/turn on a switch with a greedy heuristic:
   1) If the switch is under-utilized (less then 10% of utilization for all its links), the switch is turned off to save energy. Only aggregation switches and 
      core switches can be turned off;
   2) If a link is over-utilized (more than 70% of utilization), it attempts to turn on a deactivated switch to balance the load:
        - if the congested link is between an edge and an aggregation switch, attempt to reactivate another aggregation switch in the same herd;
        - if the congested link is between an aggregation and a core switch, attempt to reactivate a core switch;
   @param Mininet net
   @param FatTree topo'''
def turn_off_switch_greedy(net, topo):
    global active_switches, deactivation_count, url, base_interval, min_interval, max_interval

    with open(log_path, "w") as log_file:
        log_file.write(f"{dt.now()} -> Initialize control loop for turning off/on topology switches\n")
        log_file.write(f"{dt.now()} -> Energy-aware optimization with greedy heuristic\n")
        log_file.write(f"\n")

    #initialize dictionaries at first execution
    for a in topo.get_layer_nodes(FatTree.agg_layer()): #add aggregation switches to the dictionary
        active_switches[a]=True #switch is active in the DCN
        deactivation_count[a]=0 #switch can be deactivated
    for c in topo.get_layer_nodes(FatTree.core_layer()): #add core switches to the dictionary
        active_switches[c]=True #switch is active in the DCN
        deactivation_count[c]=0 #switch can be deactivated

    time.sleep(200) #initial waiting time
    monitoring_interval=210 #initial value of application monitoring interval
    while True:
        try:
            response=requests.get(url) #fetch current link stats from REST API endpoint through HTTP GET
            if response.status_code==200: #if the get request is successful
                data_dic=response.json() #fetch data in JSON format and save them in a dictionary
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Acquiring link utilization data\n")
                    log_file.write(f"\n")

                for a in topo.get_layer_nodes(FatTree.agg_layer()): #for all aggregation switches
                    links_name={} #dictionary <link_name: float> (register the utilization rate for all links of the current agg switch)
                    for e in topo.get_down_nodes(a): #for all edge switches connected to current aggregation switch
                        links_name[f'{e}-{a}']=0 #initialize utilization rate at 0
                    for c in topo.get_up_nodes(a): #for all core switches connected to current aggregation switch
                        links_name[f'{a}-{c}']=0 #initialize utilization rate at 0
                    for link in links_name.keys(): #fetch utilization rate for each link from response data
                        links_name[link]=next((item["utilization"] for item in data_dic if item["link_name"]==link), 0)

                        if links_name[link]>0.7: #if the link is over-utilized (utilization rate over 70%)
                            with open(log_path, "a") as log_file:
                                log_file.write(f"{dt.now()} -> Link {link} is over-utilized. Attempt to re-activate a switch.\n")

                            if link.startswith(a): #if the link is agg-core, try to turn on a core switch
                                inactive_core_switches=[s for s in topo.get_layer_nodes(FatTree.core_layer()) if active_switches[s]==False] #cores currently off
                                with open(log_path, "a") as log_file:
                                    log_file.write(f"{dt.now()} -> inactive_core_switches {inactive_core_switches} \n")

                                if len(inactive_core_switches)>0: #if there is at least one core currently off
                                    target=random.choice(inactive_core_switches) #choose a core to turn on
                                    sw=net.getNodeByName(target) #get reference to Mininet Node object to turn on
                                    down_neighbors=[n for n in topo.get_down_nodes(target) if active_switches[n]==True] #active down neighbors of target core
                                    for neighbor in down_neighbors: #connect target core switch with active aggregation switches (down neighbors)
                                        net.addLink(node1=sw, node2=net.getNodeByName(neighbor),
                                                    port1=topo.port(target, neighbor)[0],
                                                    port2=topo.port(target, neighbor)[1],
                                                    cls=TCLink, bw=topo.bw[FatTree.core_layer()],
                                                    loss=topo.loss[FatTree.core_layer()],
                                                    delay=topo.delay[FatTree.core_layer()],
                                                    jitter=topo.jitter[FatTree.core_layer()],
                                                    max_queue_size=topo.max_queue[FatTree.core_layer()])
                                        with open(log_path, "a") as log_file:
                                            log_file.write(f"{dt.now()} -> Link between core switch {target} and aggregation switch {neighbor} reactivated.\n")

                                    sw.start([RemoteController('c0', ip="localhost", port=6653)]) #restart target core switch
                                    active_switches[target]=True #mark target core switch as active
                                    deactivation_count[target]=2 #target core switch cannot be deactivated for at least 2 rounds
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Switch {target} ({sw.dpid}) reactivated.\n")
                                else: #if there is no core switch turned off that can be reactivated
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> No core switch is inactive.\n")

                            else: #if the link is edge-agg, try to turn on another aggregation switch in the same herd
                                inactive_agg_switches=[s for s in topo.get_layer_nodes(FatTree.agg_layer()) if active_switches[s]==False
                                                       and topo.get_herd_id(s)==topo.get_herd_id(a)] #agg switches currently off in the herd

                                with open(log_path, "a") as log_file:
                                    log_file.write(f"{dt.now()} -> inactive_agg_switches {inactive_agg_switches} \n")

                                if len(inactive_agg_switches)>0: #if there is at least one aggregation switch in the herd currently inactive
                                    target=random.choice(inactive_agg_switches) #choose an agg switch to turn on
                                    sw=net.getNodeByName(target) #get reference to Mininet Node to turn on
                                    down_neighbors=[n for n in topo.get_down_nodes(target)] #list of all edge switches connected to target agg switch
                                    up_neighbors=[n for n in topo.get_up_nodes(target) if active_switches[n]==True] #core switches connected to target agg switch
                                    for neighbor in down_neighbors: #connect target agg switch with edge switches (down neighbors)
                                        net.addLink(node1=sw, node2=net.getNodeByName(neighbor),
                                                    port1=topo.port(target, neighbor)[0],
                                                    port2=topo.port(target, neighbor)[1],
                                                    cls=TCLink, bw=topo.bw[FatTree.agg_layer()],
                                                    loss=topo.loss[FatTree.agg_layer()],
                                                    delay=topo.delay[FatTree.agg_layer()],
                                                    jitter=topo.jitter[FatTree.agg_layer()],
                                                    max_queue_size=topo.max_queue[FatTree.agg_layer()])
                                        with open(log_path, "a") as log_file:
                                            log_file.write(f"{dt.now()} -> Link between aggregation switch {target} and edge switch {neighbor} reactivated.\n")
                                    for neighbor in up_neighbors: #connect target agg switch with active core switches (up neighbors)
                                        net.addLink(node1=sw, node2=net.getNodeByName(neighbor),
                                                    port1=topo.port(target, neighbor)[0],
                                                    port2=topo.port(target, neighbor)[1],
                                                    cls=TCLink, bw=topo.bw[FatTree.core_layer()],
                                                    loss=topo.loss[FatTree.core_layer()],
                                                    delay=topo.delay[FatTree.core_layer()],
                                                    jitter=topo.jitter[FatTree.core_layer()],
                                                    max_queue_size=topo.max_queue[FatTree.core_layer()])
                                        with open(log_path, "a") as log_file:
                                            log_file.write(f"{dt.now()} -> Link between aggregation switch {target} and core switch {neighbor} reactivated.\n")

                                    sw.start([RemoteController('c0', ip="localhost", port=6653)]) #restart target agg switch
                                    active_switches[target]=True #mark target agg switch as active
                                    deactivation_count[target]=2 #target agg switch cannot be deactivated for at least 2 round
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Switch {target} ({sw.dpid}) reactivated.\n")
                                else: #if there is no aggregation switch turned off that can be reactivated
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> No aggregation switch is inactive.\n")

                    utilization_values=[links_name[l] for l in links_name.keys() if links_name[l]] #utilization rates for all links of current agg switch
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> Links utilization for switch {a}: {utilization_values}\n")
                    if len(utilization_values)!=0 and all(value<0.1 for value in utilization_values): #if all links of the switch are under-utilized (<10%)
                        active_switches_herd=[s for s in topo.get_layer_nodes(FatTree.agg_layer()) if topo.get_herd_id(s)==topo.get_herd_id(a) and
                                             active_switches[s]==True] #list of all active aggregation switches in the herd
                        if a!=active_switches_herd[0]: #we can turn off the agg switch if it is not the first in the herd (must be kept active)
                            if deactivation_count[a]!=0: #if the agg switch cannot be deactivated in this round
                                deactivation_count[a]-=1 #decrement deactivation count for the switch
                            else: #if the agg switch can be deactivated
                                active_switches[a]=False #set the switch as turned off
                                sw=net.getNodeByName(a) #get reference to Mininet Node to turn off
                                with open(log_path, "a") as log_file:
                                    log_file.write(f"{dt.now()} -> Switch {a} ({sw.dpid}) is under-utilized. We will turn it off.\n")

                                down_neighbors=[n for n in topo.get_down_nodes(a)] #list of edge switches connected to current agg switch
                                up_neighbors=[n for n in topo.get_up_nodes(a) if active_switches[n]==True] #list of core switches connected to current agg switch
                                for neighbor in down_neighbors: #for all connected edge switches
                                    net.delLinkBetween(sw, net.getNodeByName(neighbor)) #remove agg-edge link from network
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Link between aggregation switch {a} and edge switch {neighbor} is de-activated.\n")
                                for neighbor in up_neighbors: #for all connected core switches
                                    net.delLinkBetween(sw, net.getNodeByName(neighbor)) #remove agg-core link from network
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Link between aggregation switch {a} and core switch {neighbor} is de-activated.\n")
                                sw.stop() #turn off agg switch

                for c in topo.get_layer_nodes(topo.core_layer()): #for all core switches
                    links_name={} #dictionary <link_name: float> (register the utilization rate for all links of the current core switch)
                    for a in topo.get_down_nodes(c): #for all aggregation switches connected to current core switch (down neighbors)
                        links_name[f'{a}-{c}']=0 #initialize link utilization rate to 0
                    for link in links_name.keys(): #fetch utilization rate for each link from response data
                        links_name[link]=next((item["utilization"] for item in data_dic if item["link_name"]==link), 0)

                        if links_name[link]>0.7: #if the link is over-utilized (utilization rate over 70%)
                            with open(log_path, "a") as log_file:
                                log_file.write(f"{dt.now()} -> Link {link} is over-utilized. Attempt to re-activate a switch.\n")

                            inactive_core_switches=[s for s in topo.get_layer_nodes(FatTree.core_layer()) if active_switches[s]==False] #core sw currently off
                            with open(log_path, "a") as log_file:
                                log_file.write(f"{dt.now()} -> inactive_core_switches {inactive_core_switches} \n")

                            if len(inactive_core_switches)>0: #if there is at least one core currently off
                                target=random.choice(inactive_core_switches) #choose a core switch to reactivate
                                sw=net.getNodeByName(target) #get reference to Mininet Node to turn on
                                down_neighbors=[n for n in topo.get_down_nodes(target) if active_switches[n]==True] #all agg switches connected to target core
                                for neighbor in down_neighbors: #re-establish agg-core links
                                    net.addLink(node1=sw, node2=net.getNodeByName(neighbor),
                                                port1=topo.port(target, neighbor)[0],
                                                port2=topo.port(target, neighbor)[1],
                                                cls=TCLink, bw=topo.bw[FatTree.core_layer()],
                                                loss=topo.loss[FatTree.core_layer()],
                                                delay=topo.delay[FatTree.core_layer()],
                                                jitter=topo.jitter[FatTree.core_layer()],
                                                max_queue_size=topo.max_queue[FatTree.core_layer()])
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Link between core switch {target} and aggregation switch {neighbor} reactivated.\n")

                                sw.start([RemoteController('c0', ip="localhost", port=6653)]) #restart target core switch
                                active_switches[target]=True #mark target core switch as active
                                deactivation_count[target]=2 #target core switch cannot be deactivated for at least 2 rounds
                                with open(log_path, "a") as log_file:
                                    log_file.write(f"{dt.now()} -> Switch {target} ({sw.dpid}) reactivated.\n")
                            else: #if there is no core switch turned off that can be reactivated
                                with open(log_path, "a") as log_file:
                                    log_file.write(f"{dt.now()} -> No core switch is inactive.\n")

                    utilization_values=[links_name[l] for l in links_name.keys() if links_name[l]] #utilization rates for all links of current core switch
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> Link utilization for switch {c}: {utilization_values}\n")

                    if len(utilization_values)!=0 and all(value<0.1 for value in utilization_values): #if all links of the switch are under-utilized (<10%)
                        active_switches_core=[s for s in topo.get_layer_nodes(topo.core_layer()) if active_switches[s]==True] #list of active core switches
                        if c!=active_switches_core[0]: #we can turn down the first core switch (to ensure reachability)
                            if deactivation_count[c]!=0: #if the current core switch cannot be deactivated in this round
                                deactivation_count[c]-=1 #decrement deactivation count for the current core switch
                            else: #if the current core switch can be deactivated in this round
                                active_switches[c]=False #mark current core switch as inactive
                                sw=net.getNodeByName(c) #get reference to Mininet Node to turn off
                                with open(log_path, "a") as log_file:
                                    log_file.write(f"{dt.now()} -> Switch {c} ({sw.dpid}) is under-utilized. We will turn it off.\n")

                                down_neighbors=[n for n in topo.get_down_nodes(c) if active_switches[n]==True] #all active agg sw connected to current core sw
                                for neighbor in down_neighbors: #for all connected agg switches (down neighbors)
                                    net.delLinkBetween(sw, net.getNodeByName(neighbor)) #remove link between agg switch and current core switch
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Link between core switch {c} and aggregation switch {neighbor} is de-activated.\n")

                                sw.stop() #turn off current core switch

                #Adaptive monitoring period algorithm
                loads=[entry["utilization"] for entry in data_dic] #bandwidth utilization for all network's links
                alpha=0.5 #coefficient weighting average utilization and maximum utilization in the network's overall utilization stimate

                assert all(0<=utilization<=1 for utilization in loads), "Some utilization values exceed the interval [0,1]"
                try:
                    average_load=sum(loads)/len(loads) #average link's utilization
                except ZeroDivisionError:
                    average_load=0
                try:
                    max_load=max(loads) #maximum link utilization
                except ValueError:
                    max_load=0
                network_load=alpha*average_load+(1-alpha)*max_load #estimate of network's overall link utilization
                with open(log_path, "a") as log_file:
                    log_file.write(f'\n')
                    log_file.write(f"{dt.now()} -> Average link utilization: {average_load}, max link utilization: {max_load}, "
                                   f"network_utilization: {network_load}.\n")

                monitoring_interval=-base_interval*math.log2(network_load) #dynamically change monitoring period according to network's utilization
                if monitoring_interval<min_interval: #if monitoring interval is decreasing below a set lower-bound
                    monitoring_interval=min_interval #set monitoring interval to lower-bound
                elif monitoring_interval>max_interval: #if monitoring interval is increasing over a set upper-bound
                    monitoring_interval=max_interval #set monitoring interval to upper-bound
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> New monitoring interval: {monitoring_interval}.\n")
                    log_file.write(f'\n')

            else: #if GET HTTP request is unsuccessful
                print(f"Error in HTTP request {response.status_code}: {response.text}")
        except Exception as e:
            print(f"{e}")

        time.sleep(monitoring_interval) #thread sleeps for a period before issuing a new HTTP request and repeating the control loop

'''Thread target function. Periodically, it fetches current link stats from Ryu controller (which exposes data through a REST API). According to link status,
   it decides whether to turn off a switch (either aggregation or core) with a probabilistic heuristic: 
   1) if the switch is under-utilized (less then 50% of utilization for all its links), we assign to it a "turn off probability" equal to 1 minus the average 
      utilization rate of its links (so, the less utilized is the switch, the higher is the probability of turning it off). After evaluating all switches, a 
      random value "turn off" in the [0,1] interval is extracted and if the turn off probability of a given switch is higher then the turn off value, the switch 
      will be de-activated. The first aggregation switch in each herd and the first core switch cannot be de-activated to guarantee connectivity;
   2) If a link is over-utilized (more than 70% of utilization), it attempts to turn on greedily a deactivated switch to balance the load:
         - if the congested link is between and edge and an aggregation switch, attempt to reactivate another aggregation switch in the same herd;
         - if the congested link is between an aggregation and a core switch, attempt to re-activate a core switch;
   @param Mininet net
   @param FatTree topo'''
def turn_off_switch_probabilistic(net, topo):
    global active_switches, deactivation_count, turn_off_probability, url, base_interval, min_interval, max_interval

    with open(log_path, "w") as log_file:
        log_file.write(f"{dt.now()} -> Initialize control loop for turning off/on topology switches\n")
        log_file.write(f"{dt.now()} -> Energy-aware optimization with probability-based heuristic\n")
        log_file.write(f"\n")

    #initialize dictionaries before looping
    for a in topo.get_layer_nodes(topo.agg_layer()): #for all agg switches
        active_switches[a]=True #switch is active
        deactivation_count[a]=0 #switch can be deactivated
    for c in topo.get_layer_nodes(topo.core_layer()): #for all core switches
        active_switches[c]=True #switch is active
        deactivation_count[c]=0 #switch can be deactivated
    for switch in active_switches.keys(): #for all agg and core switches
        turn_off_probability[switch]=0 #switch deactivation probability is zero

    time.sleep(200) #initial waiting time
    monitoring_interval=210 #initial value of application monitoring interval
    while True:
        try:
            response=requests.get(url) #HTTP GET request on REST API endpoint
            if response.status_code==200: #if request is successful
                data_dic=response.json() #fetch link stats data in JSON format and save them as dictionary
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Current link status data: \n")
                    log_file.write(f"\n")

                for a in topo.get_layer_nodes(FatTree.agg_layer()): #for all agg switches
                    links_name={} #dictionary <link_name: float> (register the utilization rate for all links of the current agg switch)
                    for e in topo.get_down_nodes(a): #for all downward links (towards edges)
                        links_name[f'{e}-{a}']=0 #initialize link utilization rate at 0
                    for c in topo.get_up_nodes(a): #for all upward links (towards cores)
                        links_name[f'{a}-{c}']=0 #initialize link utilization at 0
                    for link in links_name.keys(): #for each link of the current agg switch, fetch current utilization rate from response data
                        links_name[link]=next((item["utilization"] for item in data_dic if item["link_name"]==link), 0)

                        if links_name[link]>0.7: #if the link is over-utilized
                            with open(log_path, "a") as log_file:
                                log_file.write(f"{dt.now()} -> Link {link} is over-utilized. Attempt to re-activate a switch.\n")

                            if link.startswith(a): #if the link is agg-core, attempt to reactivate a core
                                inactive_core_switches=[s for s in topo.get_layer_nodes(topo.core_layer()) if active_switches[s]==False] #currently off core sw
                                with open(log_path, "a") as log_file:
                                    log_file.write(f"{dt.now()} -> inactive_core_switches {inactive_core_switches} \n")

                                if len(inactive_core_switches)>0: #if there is at least 1 core switch currently off
                                    target=random.choice(inactive_core_switches) #choose randomly a core switch to reactivate (target)
                                    sw=net.getNodeByName(target) #get Mininet Node reference
                                    down_neighbors=[n for n in topo.get_down_nodes(target) if active_switches[n]==True] #agg switches connected to target core
                                    for neighbor in down_neighbors: #restablish agg-core links for target core
                                        net.addLink(node1=sw, node2=net.getNodeByName(neighbor),
                                                    port1=topo.port(target, neighbor)[0],
                                                    port2=topo.port(target, neighbor)[1],
                                                    cls=TCLink, bw=topo.bw[FatTree.core_layer()],
                                                    loss=topo.loss[FatTree.core_layer()],
                                                    delay=topo.delay[FatTree.core_layer()],
                                                    jitter=topo.jitter[FatTree.core_layer()],
                                                    max_queue_size=topo.max_queue[FatTree.core_layer()])
                                        with open(log_path, "a") as log_file:
                                            log_file.write(f"{dt.now()} -> Link between core switch {target} and aggregation switch {neighbor} reactivated.\n")

                                    sw.start([RemoteController('c0', ip="localhost", port=6653)]) #restart target core
                                    active_switches[target]=True #mark target core as active
                                    deactivation_count[target]=2 #target core cannot be deactivated for at least 2 rounds
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Switch {target} ({sw.dpid}) reactivated.\n")
                                else: #if there is no core switch turned off that can be reactivated
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> No core switch is inactive.\n")

                            else: #if the link is edge-agg, attempt to reactivate an agg switch in the same herd
                                inactive_agg_switches=[s for s in topo.get_layer_nodes(FatTree.agg_layer()) if active_switches[s]==False
                                                       and topo.get_herd_id(s)==topo.get_herd_id(a)] #currently inactive agg switches in the herd
                                with open(log_path, "a") as log_file:
                                    log_file.write(f"{dt.now()} -> inactive_agg_switches {inactive_agg_switches} \n")

                                if len(inactive_agg_switches)>0: #if there is at least 1 inactive agg switch in the herd
                                    target=random.choice(inactive_agg_switches) #choose agg switch to reactivate randomly (target)
                                    sw=net.getNodeByName(target) #get Mininet Node reference
                                    down_neighbors=[n for n in topo.get_down_nodes(target)] #all edge switches connected to target agg switch
                                    up_neighbors=[n for n in topo.get_up_nodes(target) if active_switches[n]==True] #all active core connected to target agg
                                    for neighbor in down_neighbors: #for all connected edge switches, reestablish link with target agg
                                        net.addLink(node1=sw, node2=net.getNodeByName(neighbor),
                                                    port1=topo.port(target, neighbor)[0],
                                                    port2=topo.port(target, neighbor)[1],
                                                    cls=TCLink, bw=topo.bw[FatTree.agg_layer()],
                                                    loss=topo.loss[FatTree.agg_layer()],
                                                    delay=topo.delay[FatTree.agg_layer()],
                                                    jitter=topo.jitter[FatTree.agg_layer()],
                                                    max_queue_size=topo.max_queue[FatTree.agg_layer()])
                                        with open(log_path, "a") as log_file:
                                            log_file.write(f"{dt.now()} -> Link between aggregation switch {target} and edge switch {neighbor} reactivated.\n")
                                    for neighbor in up_neighbors: #for all connected cores, reestablish link with target agg
                                        net.addLink(node1=sw, node2=net.getNodeByName(neighbor),
                                                    port1=topo.port(target, neighbor)[0],
                                                    port2=topo.port(target, neighbor)[1],
                                                    cls=TCLink, bw=topo.bw[FatTree.core_layer()],
                                                    loss=topo.loss[FatTree.core_layer()],
                                                    delay=topo.delay[FatTree.core_layer()],
                                                    jitter=topo.jitter[FatTree.core_layer()],
                                                    max_queue_size=topo.max_queue[FatTree.core_layer()])
                                        with open(log_path, "a") as log_file:
                                            log_file.write(f"{dt.now()} -> Link between aggregation switch {target} and core switch {neighbor} reactivated.\n")
                                    sw.start([RemoteController('c0', ip="localhost", port=6653)]) #restart target agg switch
                                    active_switches[target]=True #mark target agg switch as active
                                    deactivation_count[target]=2 #target agg switch cannot be deactivated for at least 2 rounds
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Switch {target} ({sw.dpid}) reactivated.\n")
                                else: #if there is no aggregation switch turned off that can be reactivated in the herd
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> No aggregation switch is inactive.\n")

                    utilization_values=[links_name[l] for l in links_name.keys() if links_name[l]] #link utilization rate of all links of current agg switch
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> Link utilization for switch {a}: {utilization_values}\n")

                    if len(utilization_values)!=0 and all(value<0.5 for value in utilization_values): #if all links are below 50% utilization
                        agg_switches_herd=[s for s in topo.get_layer_nodes(topo.agg_layer()) if topo.get_herd_id(s)==topo.get_herd_id(a)] #active agg sw in the herd
                        if a!=agg_switches_herd[0]: #if the current agg switch is not the first in the herd (needs to be maintained for reachability)
                            turn_off_probability[a]=1-(sum(utilization_values)/len(utilization_values)) #compute turn off probability for current agg switch

                for c in topo.get_layer_nodes(topo.core_layer()): #for all core switches
                    links_name={} #dictionary <link_name: float> (register the utilization rate for all links of the current core switch)
                    for a in topo.get_down_nodes(c): #for all agg-core links of current core
                        links_name[f'{a}-{c}']=0 #initialize link utilization rate

                    for link in links_name.keys(): #for all links of current core, fetch link utilization rate from response data
                        links_name[link]=next((item["utilization"] for item in data_dic if item["link_name"]==link), 0)

                        if links_name[link]>0.7: #if the link is over-utilized, attempt to reactivate a core switch
                            with open(log_path, "a") as log_file:
                                log_file.write(f"{dt.now()} -> Link {link} is over-utilized. Attempt to re-activate a switch.\n")

                            inactive_core_switches=[s for s in topo.get_layer_nodes(FatTree.core_layer()) if active_switches[s]==False] #currently off cores
                            with open(log_path, "a") as log_file:
                                log_file.write(f"{dt.now()} -> inactive_core_switches {inactive_core_switches} \n")

                            if len(inactive_core_switches)>0: #if there is at least one core to reactivate
                                target=random.choice(inactive_core_switches) #choose randomly core to reactivate (target)
                                sw=net.getNodeByName(target) #get Mininet Node reference
                                down_neighbors=[n for n in topo.get_down_nodes(target) if active_switches[n]==True] #all agg switches connected to target core
                                for neighbor in down_neighbors: #reestablish links target core-agg switches
                                    net.addLink(node1=sw, node2=net.getNodeByName(neighbor),
                                                port1=topo.port(target, neighbor)[0],
                                                port2=topo.port(target, neighbor)[1],
                                                cls=TCLink, bw=topo.bw[FatTree.core_layer()],
                                                loss=topo.loss[FatTree.core_layer()],
                                                delay=topo.delay[FatTree.core_layer()],
                                                jitter=topo.jitter[FatTree.core_layer()],
                                                max_queue_size=topo.max_queue[FatTree.core_layer()])
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Link between core switch {target} and aggregation switch {neighbor} reactivated.\n")

                                sw.start([RemoteController('c0', ip="localhost", port=6653)]) #restart target core
                                active_switches[target]=True #mark target core as active
                                deactivation_count[target]=2 #target core cannot be deactivated for at least 2 rounds
                                with open(log_path, "a") as log_file:
                                    log_file.write(f"{dt.now()} -> Switch {target} ({sw.dpid}) reactivated.\n")

                    utilization_values=[links_name[l] for l in links_name.keys() if links_name[l]] #utilization rates for all links of current core
                    with open(log_path, "a") as log_file:
                        log_file.write(f"{dt.now()} -> Link utilization for switch {c}: {utilization_values}\n")

                    if len(utilization_values)!=0 and all(value<0.5 for value in utilization_values): #if all links have utilization below 50%
                        core_switches=[s for s in topo.get_layer_nodes(topo.core_layer())] #topology core switches
                        if c!=core_switches[0]: #if the current core switch is not the first (it cannot be turned off for reachability)
                            turn_off_probability[c]=1-(sum(utilization_values)/len(utilization_values)) #compute turn off probability for current core

                #turn off probability of first core and first agg in each herd is 0, meaning they cannot be turned off for reachability reasons

                turn_off=random.random() #select turn off value
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> Probabilities of turning off: {turn_off_probability}.\n")
                    log_file.write(f"{dt.now()} -> Extracted value: {turn_off}.\n")

                for switch in turn_off_probability.keys(): #for all switches that can be turned off (agg and core)
                    if active_switches[switch]==True and turn_off<=turn_off_probability[switch]: #the switch is selected to be turned off
                        sw=net.getNodeByName(switch) #get Mininet Node reference
                        with open(log_path, "a") as log_file:
                            log_file.write(f"{dt.now()} -> Switch {switch} ({sw.dpid}) is under-utilized. We will turn it off.\n")

                        if topo.get_herd_id(switch)==topo.k: #if the current switch is at core level
                            if deactivation_count[switch]!=0: #if the current switch cannot be deactivated in this round
                                deactivation_count[switch]-=1 #decrement deactivation count for current switch
                            else: #if current switch can be deactivated in this round
                                down_neighbors=[n for n in topo.get_down_nodes(switch) if active_switches[n]==True] #active agg sw connected to current core sw
                                for neighbor in down_neighbors: #for all connected agg switches
                                    net.delLinkBetween(sw, net.getNodeByName(neighbor)) #remove agg-core link
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Link between core switch {switch} and aggregation switch {neighbor} is de-activated.\n")

                                sw.stop() #turn off current core switch
                                active_switches[switch]=False #mark current core switch as inactive
                                turn_off_probability[switch]=0 #reset turn off probability
                        else: #if the current switch is at aggregation level
                            if deactivation_count[switch]!=0: #if current switch cannot be deactivated in this round
                                deactivation_count[switch]-=1 #decrement deactivation count for current switch
                            else: #if current switch can be deactivated in this round
                                down_neighbors=[n for n in topo.get_down_nodes(switch)] #all edge switches connected to current agg switch
                                up_neighbors=[n for n in topo.get_up_nodes(switch) if active_switches[n]==True] #all active cores connected to current agg switch
                                for neighbor in down_neighbors: #for all connected edge switches
                                    net.delLinkBetween(sw, net.getNodeByName(neighbor)) #remove agg-edge link from network
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Link between aggregation switch {switch} and edge switch {neighbor} is de-activated.\n")
                                for neighbor in up_neighbors: #for all connected core switches
                                    net.delLinkBetween(sw, net.getNodeByName(neighbor)) #remove agg-core link from network
                                    with open(log_path, "a") as log_file:
                                        log_file.write(f"{dt.now()} -> Link between aggregation switch {switch} and core switch {neighbor} is de-activated.\n")

                                sw.stop() #turn off current aggregation switch
                                active_switches[switch]=False #mark current aggregation sw as inactive
                                turn_off_probability[switch]=0 #reset turn off probability for current agg switch

                #Adaptive monitoring period algorithm
                loads=[entry["utilization"] for entry in data_dic] #bandwidth utilization for all network's links
                alpha=0.5 #coefficient weighting average utilization and maximum utilization in the network overall utilization estimate

                assert all(0<=utilization<=1 for utilization in loads), "Some utilization rates exceed the interval [0,1]"
                try:
                    average_load=sum(loads)/len(loads) #average link's utilization
                except ZeroDivisionError:
                    average_load=0
                try:
                    max_load=max(loads) #maximum link utilization
                except ValueError:
                    max_load=0
                network_load=alpha*average_load+(1-alpha)*max_load #estimate of network's overall link utilization
                with open(log_path, "a") as log_file:
                    log_file.write(f'\n')
                    log_file.write(f"{dt.now()} -> Average link utilization: {average_load}, max link utilization: {max_load}, "
                                   f"network_utilization: {network_load}.\n")

                monitoring_interval=-base_interval*math.log2(network_load) #dynamically change monitoring period according to network's utilization
                if monitoring_interval<min_interval: #if monitoring interval is decreasing below a set lower-bound
                    monitoring_interval=min_interval #set monitoring interval to lower-bound
                elif monitoring_interval>max_interval: #if monitoring interval is increasing over a set upper-bound
                    monitoring_interval=max_interval #set monitoring interval to upper-bound
                with open(log_path, "a") as log_file:
                    log_file.write(f"{dt.now()} -> New monitoring interval: {monitoring_interval}.\n")
                    log_file.write(f'\n')

            else: #if GET HTTP request is unsuccessful
                print(f"Error in HTTP request {response.status_code}: {response.text}")
        except Exception as e:
            print(f"{e}")

        time.sleep(monitoring_interval) #threa sleeps for a period before issuing a new HTTP request and repeating the control loop

############################################################################################Traffic generation functions
'''Debugging code testing basic connectivity in the deployed topology
   @param Mininet net
   @param FatTree topo'''
def debug_routing(net, topo):
    assert isinstance(net, Mininet), f"Expected instance of Mininet, got {type(net)} instead"
    assert isinstance(topo, FatTree), f"Expected instance of FatTree, got {type(topo)} instead"

    print('Perform ping test:')
    net.pingAll() #reachability test between all pairs of servers in the network
    print('\n')

'''Debugging code testing basic broadcasting functionality on deployed topology
   @param Mininet net
   @param FatTree topo'''
def debug_broadcast(net, topo):
    assert isinstance(net, Mininet), f"Expected instance of Mininet, got {type(net)} instead"
    assert isinstance(topo, FatTree), f"Expected instance of FatTree, got {type(topo)} instead"

    for server in net.hosts: #apply sysctl settings to all servers (host devices)
        server.cmd('sysctl -p') # disable ignore_icmp_broadcast on servers

    for sw in topo.get_layer_nodes(FatTree.edge_layer()): #for all edge switches
        obj=net.getNodeByName(sw) #get reference to OVS switch object (Mininet Switch)
        for intf in obj.intfList()[1:(topo.k//2)+1]: #for each downward interface of edge switch (towards servers), numbered from 1 to k/2
            obj.cmd("pkill -f 'tcpdump'") #terminate lingering tcpdump process
            obj.cmd(f'rm -f /tmp/{intf}.pcap') #remove old tcpdump capture files

            print(f"Starting tcpdump on {intf}...")
            obj.cmd(f'tcpdump -i {intf} icmp -nn -w /tmp/{intf}.pcap 2>/dev/null &') #start tcpdump in background on switch shell, saving captured ICMP messages

    print('\n')
    time.sleep(1) #Allow tcpdump to start
    ping_src=net.hosts[random.randint(0, len(net.hosts)-1)] #choose randomly a server in the datacenter from where to ping broadcast
    print(f"Broadcasting from {ping_src.name}...\n")
    ping_src.cmd(f'ping -b -c 2 {topo.broadcast_address}') #issue broadcast ping command on emulated server shell (blocking)
    time.sleep(10) #Wait for tcpdump to capture ICMP traffic

    for sw in topo.get_layer_nodes(FatTree.edge_layer()): #for all edge switches
        obj=net.getNodeByName(sw) #get reference to OVS switch object (Mininet Switch)
        for intf in obj.intfList()[1:(topo.k//2)+1]: #for each downward interface of edge switch (towards servers), numbered from 1 to k/2
            obj.cmd("pkill -f 'tcpdump'") #stop tcpdump process
            result=obj.cmd(f'tcpdump -nn -r /tmp/{intf}.pcap') #read packets ICMP captured by tcpdump
            print(f"Captured packets on {intf}:\n{result}\n") #print captured packets on terminal

'''Send background broadcast traffic using Hping3 from a server in the topology
   @param str source_server
   @param Mininet net
   @param FatTree topo
   @param int src_port
   @param int dst_port'''
def send_broadcast(source_server, net, topo, src_port, dst_port):
    assert isinstance(net, Mininet), f"Expected instance of Mininet class, got {type(net)} instead"
    assert isinstance(topo, FatTree), f"Expected instance of FatTree class, got {type(topo)} instead"

    duration=30*60 #simulation time (seconds)
    interleave_time=0.1 #interleave between packets (seconds)

    src_ip=topo.get_ipv4(name=source_server) #source server IPv4 address
    src=net.getNodeByName(source_server) #Mininet-emulated source server (Mininet Host Object)
    dst_ip=topo.broadcast_address #destination IPv4 address (broadcast)

    out_intf=f'{source_server}-eth1' #L2 exit interface on source server
    packet_count=duration//interleave_time #number of broadcast packets to be sent

    hping_cmd=["hping3",
               "-I", out_intf, #output L2 interface
               "-c", str(packet_count), #number of packets to send
               "-d", "1450", #payload size in bytes
               "-p", str(dst_port), #L4 destination port
               "-s", str(src_port), #L4 source port
               "-k", #fix L4 source port value
               "-a", src_ip, #source IPv4 address (spoofed)
               "-i", f"u{interleave_time*1000000}", #packet inter-arrival time (microseconds)
               "--udp", #L4 protocol (UDP for broadcast packets)
               dst_ip, ] #destination IPv4 address

    src.popen(hping_cmd, shell=True) #issue Hping command on emulated server shell (non-blocking)

'''Thread target function. Given a source server, it periodically selects a destination in the topology and instructs the Mininet-emulated server (host device) 
   to forward traffic to it (by running a Hping3 command). Transmitted flows are elephants
   @param str source_server
   @param Mininet net
   @param FatTree topo
   @param int src_port
   @param int dst_port
   @param Lock lock'''
def start_elephants(source_server, net, topo, src_port, dst_port, lock):
    assert isinstance(net, Mininet), f"Expected instance of Mininet class, got {type(net)} instead"
    assert isinstance(topo, FatTree), f"Expected instance of FatTree class, got {type(topo)} instead"

    duration=15 #simulation time (minutes)
    start_time=time.time() #record of simulation starting time
    time.sleep(generate_inter_start_time(mean=180, dev=10, lower_bound=175, upper_bound=185)) #random waiting interval

    src_ip=topo.get_ipv4(name=source_server) #source server IPv4 address
    src=net.getNodeByName(source_server) #Mininet-emulated source server (Mininet Host reference)

    while time.time()-start_time<duration*60: #for the whole duration
        if random.random()<0.5: #choose casually whether to adopt TCP or UDP as L4 protocol
            l4_protocol="UDP"
        else:
            l4_protocol="TCP"

        destination_server=choose_destination(source_server, topo, [0,0]) #select a destination server according to staggered probability
        dst_ip=topo.get_ipv4(name=destination_server) #destination server IPv4 address

        flow_size=int(np.random.uniform(100, 400)) #select elephant flow size between 100 and 400 [MB], using uniform distribution

        out_intf=f'{source_server}-eth1' #L2 exit interface on server
        packet_count=int(flow_size*(1024*1024)/1450) #number of flow packets, assuming a 1450 bytes payload

        inter_arrival_time=int(0.002*1000000) #inter-arrival time between flow packets (microseconds)

        hping_cmd=["hping3",
                   "-I", out_intf, #output L2 interface
                   "-c", str(packet_count), #number of packets to send
                   "-d", "1450", #payload size in bytes
                   "-p", str(dst_port), #L4 destination port
                   "-s", str(src_port), #L4 source port
                   "-k", #fix L4 source port value
                   "-a", src_ip, #source IPv4 address (spoofed)
                   "-i", f"u{inter_arrival_time}", #packet inter-arrival time
                    dst_ip,] #destination IPv4 address

        if l4_protocol=="TCP":
            hping_cmd.append("-P") #add TCP PUSH flag to Hping command
        elif l4_protocol=="UDP":
            hping_cmd.append("--udp") #add UDP flag to Hping command

        try:
            with lock: #ensure thread-safety when executing a new Hping shell command on Host object
                row={'flow_name': f'{src_ip}:{src_port} - {dst_ip}:{dst_port}',
                     'source': source_server,
                     'destination': destination_server,
                     'L4': l4_protocol,
                     'flow_size': flow_size, #(MB)
                     'flow_packets': packet_count,
                     'start_time': dt.now(), #record of transmission start
                     'timestamp': time.time()} #dictionary containing stats for the new elephant flow
                new_df=pd.DataFrame([row]) #convert dictionary to DataFrame

                #file_path="./DataFiles/FlowStatsSendBase.csv" #.csv file containing flow stats (benchmark controller)
                #file_path="./DataFiles/FlowStatsSendEnhanced.csv" #.csv file containing flow stats (enhanced controller)
                #file_path="./DataFiles/FlowStatsSendGreedy.csv" #.csv file containing flow stats (enhanced controller + greedy heuristic)
                file_path="./DataFiles/FlowStatsSendProb.csv" #.csv file containing flow stats (enhanced controller + probabilistic heuristic)
                file_lock=FileLock(file_path+".lock") #regulate concurrent access of multiple severs on the same .csv file
                with file_lock: #update file's content
                    file_exists=os.path.isfile(file_path) #checks if the file exists
                    new_df.to_csv(file_path, mode='a', index=False, header=not file_exists) #append new data to file if it exists, otherwise create a new file

                print(f"{dt.now()} -> Server {source_server} ({src_ip}) transmitting to server {destination_server} ({dst_ip})")

                src.popen(hping_cmd, shell=True) #issue Hping command on emulated server shell (non-blocking)
        except AssertionError as e:
            print(f"Command execution error: {e}")

        src_port+=1 #increment L4 source port for next elephant flow transmitted by the server
        dst_port+=1 #increment L4 destination port for next elephant flow transmitted by the server

        time.sleep(generate_inter_start_time(mean=210, dev=35, lower_bound=200, upper_bound=220)) #random waiting interval between elephant flows

'''Thread target function. Given a source server, it periodically selects a destination in the topology and instructs the Mininet-emulated server (host device) 
   to forward traffic to it (by running a Hping command). Transmitted flows are mice
   @param str source_server
   @param Mininet net
   @param FatTree topo
   @param int src_port
   @param int dst_port
   @param Lock lock'''
def start_mice(source_server, net, topo, src_port, dst_port, lock):
    assert isinstance(net, Mininet), f"Expected instance of Mininet class, got {type(net)} instead"
    assert isinstance(topo, FatTree), f"Expected instance of FatTree class, got {type(topo)} instead"

    duration=30 #simulation time (minutes)
    start_time=time.time() #record of simulation starting time
    time.sleep(generate_inter_start_time(mean=10, dev=10, lower_bound=5, upper_bound=15)) #random waiting interval

    src_ip=topo.get_ipv4(name=source_server) #source server IPv4 address
    src=net.getNodeByName(source_server) #Mininet-emulated source server (Mininet Host reference)

    while time.time()-start_time<duration*60:
        if random.random()<0.5: #choose casually whether to adopt TCP or UDP as L4 protocol
            l4_protocol="UDP"
        else:
            l4_protocol="TCP"

        destination_server=choose_destination(source_server, topo, [0.25,0.35]) #select a destination server according to staggered probability
        dst_ip=topo.get_ipv4(name=destination_server) #destination server IPv4 address

        #select mice flow size (between 0.1 [MB] and 80 [MB] according to Pareto distribution
        flow_size=int(generate_flow_size(50, 1, [0.8, 0.1], 0.1, 80))

        out_intf=f'{source_server}-eth1' #L2 exit interface on server
        packet_count=int(flow_size/1450) #number of flow packets (assuming a payload of 1450 bytes)

        inter_arrival_time=int(0.002*1000000) #inter-arrival time between flow packets (microseconds)

        hping_cmd=["hping3",
                   "-I", out_intf, #output L2 interface
                   "-c", str(packet_count), #number of packets to send
                   "-d", "1450", #payload size in bytes
                   "-p", str(dst_port), #L4 destination port
                   "-s", str(src_port), #L4 source port
                   "-k", #fix L4 source port value
                   "-a", src_ip, #source IPv4 address (spoofed)
                   "-i", f"u{inter_arrival_time}", #packet inter-arrival time
                    dst_ip,] #destination IPv4 address

        if l4_protocol=="TCP":
            hping_cmd.append("-P") #add TCP PUSH flag to Hping command
        elif l4_protocol=="UDP":
            hping_cmd.append("--udp") #add UDP flag to Hping command

        try:
            with lock: #ensure thread safety when executing multiple shell hping commands on the same server (Host object)
                row={'flow_name': f'{src_ip}:{src_port} - {dst_ip}:{dst_port}',
                     'source': source_server,
                     'destination': destination_server,
                     'L4': l4_protocol,
                     'flow_size': flow_size/(1024*1024), #(MB)
                     'flow_packets': packet_count,
                     'start_time': dt.now(), #record of starting transmission
                     'timestamp': time.time()} #dictionary containing stats for the new mice flow
                new_df=pd.DataFrame([row]) #convert dictionary to DataFrame object

                #file_path="./DataFiles/FlowStatsSendBase.csv" #.csv file containing flow stats (benchmark controller)
                #file_path="./DataFiles/FlowStatsSendEnhanced.csv" #.csv file containing flow stats (enhanced controller)
                #file_path="./DataFiles/FlowStatsSendGreedy.csv" #.csv file containing flow stats (enhanced controller + greedy heuristic)
                file_path="./DataFiles/FlowStatsSendProb.csv" #.csv file containing flow stats (enhanced controller + probabilistic heuristic)
                file_lock=FileLock(file_path+".lock") #regualte concurrent access to the same file by multiple servers
                with file_lock: #update file's content
                    file_exists=os.path.isfile(file_path) #checks if the file exists
                    new_df.to_csv(file_path, mode='a', index=False, header=not file_exists) #append new data to file if it exists, otherwise create a new file

                print(f"{dt.now()} -> Server {source_server} ({src_ip}) transmitting to server {destination_server} ({dst_ip})")

                src.popen(hping_cmd, shell=True) #issue Hping command on emulated server shell (non-blocking)
        except AssertionError as e:
            print(f"Command execution error: {e}")

        src_port+=1 #increment L4 source port for next mice flow transmitted by the current server
        dst_port+=1 #increment L4 destination port for next mice flow transmitted by the current server

        time.sleep(generate_inter_start_time(mean=50, dev=35, lower_bound=40, upper_bound=60)) #random waiting interval between mice flows

'''Given a source server in the topology, select a destination server according to a staggered probability pattern (P1, P2). Destination server can either be:
    1) Connected to the same edge switch of the source (with probability P1);
    2) Residing in the same herd of the source (with probability P2),
    3) Residing in a different herd (with probability 1-P1-P2);
   @param str src_server
   @param FatTree topo
   @param float[] probs
   @return str dst_server'''
def choose_destination(src_server, topo, probs):
    assert isinstance(topo, FatTree), f"Expected instance of FatTree class, got {type(topo)} instead"

    prob=random.random() #extract a probability value
    if prob<probs[0]: #select a destination on the same edge switch with probability probs[0]
        src_edge=topo.get_up_nodes(src_server)[0] #edge switch connected to source server
        destinations=[s for s in topo.get_down_nodes(src_edge) if s!=src_server] #possible destinations connected to the same edge switch
        return random.choice(destinations)

    elif prob<sum(probs): #select a destination in the same pob (but connected to a different edge switch) with probability probs[1]
        src_edge=topo.get_up_nodes(src_server)[0] #edge switch connected to source server
        destinations=[s for s in topo.get_layer_nodes(FatTree.server_layer()) if topo.get_herd_id(s)==topo.get_herd_id(src_server)
                      and s not in topo.get_down_nodes(src_edge)] #possible destinations in the same herd (but connected to a different edge switch)
        return random.choice(destinations)

    else: #select a destination in a different pob with probability 1-probs[0]-probs[1]
        destinations=[s for s in topo.get_layer_nodes(FatTree.server_layer()) if topo.get_herd_id(s)!=topo.get_herd_id(src_server)] #possible destinations
        return random.choice(destinations)

'''Generate waiting interval (in seconds) between flows according to a normal distribution of given parameters
   @param float mean
   @param float dev
   @param int lower_bound
   @param int upper_bound
   @return float extracted_time'''
def generate_inter_start_time(mean, dev, lower_bound, upper_bound):
    extracted_time=int(np.random.normal(loc=mean, scale=dev)) #generate a number from the normal distribution with given mean and standard deviation
    return np.clip(extracted_time, lower_bound, upper_bound) #ensure waiting time respects pre-defined lower and upper bounds

'''Generate a random size (in bytes) for a mice flow according to a Pareto distribution.
   Shape and scale parameters of the Pareto distribution are estimated such that the following constraints are respected:
    1) P(second_size/2 <= size <= (3/2)*second_size)=probs[0] 
    2) P(size>=first_size)=probs[1]
   @param float first_size
   @param float second_size
   @param float[] probs
   @param float min_size
   @param float max_size
   @return float size'''
def generate_flow_size(first_size, second_size, probs, min_size, max_size):
    if not 0<min_size<second_size<first_size<max_size:
        raise ValueError("Invalid sizes have been specified")

    def shape_equation(sh, sc): #define non-linear equation to solve
        return (sc/(second_size/2))**sh-(sc/((3/2)*second_size))**sh-probs[0] #first constraint as function of shape and scale

    initial_shape=np.array([1.5]) #starting value for the shape parameter
    scale=first_size*(probs[1])**(1/initial_shape[0]) #value for the scale parameter computed according to second constraint, assuming initial shape

    shape=fsolve(lambda x: shape_equation(x, scale), initial_shape)[0] #solve non linear-equation for the shape
    scale=first_size*(probs[1])**(1/shape) #recompute scale with the new shape
    size=np.clip(np.random.pareto(shape)*scale, min_size, max_size) #flow size in MB (size must be contained in a pre-defined interval [min_size, max_size])

    return size*1024*1024 #flow size in bytes

################################################################Deploy data center network and start traffic simulations
'''Update a config file for Ryu's controller, informing controller of most important parameter values of deployed topology
   @param int new_k
   @param float[] new_bw
   @param int[] new_loss
   @param str[] new_delay
   @param str[] new_jitter
   @param int[] new_max_queue
   @param bool new_arp'''
def update_controller_config(new_k, new_bw, new_loss, new_delay, new_jitter, new_max_queue, new_arp):
    file_path="./controllerConf.txt" #file containing info about deployed topology for Ryu controller
    lines=[f"k: {new_k}\n",
           f"link_bw: {new_bw}\n",
           f"link_loss: {new_loss}\n",
           f"link_delay: {new_delay}\n",
           f"link_jitter: {new_jitter}\n",
           f"link_max_queue: {new_max_queue}\n",
           f"arp: {new_arp}\n"] #updated content of configuration file
    with open(file_path, 'w') as file:
        file.writelines(lines) #write updated content back to the file
    print(f"Ryu controller's configurations updated successfully in {file_path}.")

'''Run FatTree topology in Mininet, start thread running the switch on/off heuristic, start threads generating east-west traffic on the topology from 
   Mininet-emulated servers (host devices), start/terminate Mininet CLI
   @param int k
   @param float[] link_bw
   @param int[] link_loss
   @param str[] link_delay
   @param str[] link_jitter
   @param int[] link_max_queue
   @param bool static_arp'''
def run_fattree_topology(k, link_bw, link_loss, link_delay, link_jitter, link_max_queue, static_arp):
    #update config file (Ryu controller must know deployed topology's parameters)
    update_controller_config(k, link_bw, link_loss, link_delay, link_jitter, link_max_queue, static_arp)

    topo=FatTree(k, link_bw, link_loss, link_delay, link_jitter, link_max_queue) #it calls topology object's constructor from our custom class FatTree
    net=Mininet(topo=topo, link=TCLink, controller=RemoteController, switch=OVSKernelSwitch) #it creates an instance of Mininet class (emulated network)
    net.start() #it stars Mininet deployment

    if static_arp:
        net.staticArp() #Set up static ARP entries in topology's servers (host devices)

    print('\n')
    print("Connected switches: ", len(net.switches))
    print("Connected hosts: ", len(net.hosts))
    print("Active links: ", len(net.links))
    print('\n')

    t=threading.Thread(target=turn_off_switch_probabilistic, args=(net, topo), daemon=True) #thread running switch on/off heuristic
    t.start()

    print('Testing basic unicast connectivity\n')
    time.sleep(30) #wait controller's boot-up and installation of proactive flow rules
    debug_routing(net, topo) #testing basic connectivity
    print('Testing basic broadcast functionality\n')
    time.sleep(10)
    debug_broadcast(net, topo)

    print('Simulating east-west traffic on the network\n')
    sources=topo.get_layer_nodes(FatTree.server_layer())  #list of all servers in the data center
    transmitting_elephants=[] #threads periodically transmitting elephant flows
    transmitting_mice=[] #threads periodically transmitting mice flows

    try: #starting threads
        broadcast_port=54321 #L4 destination port for broadcast packets
        for s in sources: #for each server in the datacenter
            src=net.getNodeByName(s) #Mininet-emulated server (Host reference)

            #execute Scapy script (in background) on current server's shell to detect elephant flows among transmitted flows
            src.cmd(f'python3 DetectElephant.py --server={s} --ipv4={topo.get_ipv4(name=s)} > /tmp/{s}_detect.log 2>&1 &')

            print(f"Starting broadcast traffic from {s}\n")
            send_broadcast(s, net, topo, 12345, broadcast_port)
            broadcast_port+=1 #increment L4 broadcast destination port for next server

            lock=threading.Lock() #create Lock object for current server

            if topo.get_herd_id(s)==0: #if current server resides in the first herd
                #thread for transmitting elephant flows from current server to a server in another herd
                t_send=threading.Thread(target=start_elephants, args=(s, net, topo, 12346, 54336, lock))
                transmitting_elephants.append(t_send)
                t_send.start() #start sending thread

            else: #if current server resides in any herd other than the first
                #thread for transmitting mice flows from current server to another server in the fat-tree topology
                t_send=threading.Thread(target=start_mice, args=(s, net, topo, 13346, 55336, lock))
                transmitting_mice.append(t_send)
                t_send.start() #start sending thread

        for t_send in transmitting_elephants:
            t_send.join() #waits for all transmitting threads to finish

        print("No more elephant flows are being sent\n")

        for t_send in transmitting_mice:
            t_send.join() #waits for all transmitting threads to finish

        print("All threads finished. Traffic simulation has ended\n")
    except Exception as e:
        print(e)

    CLI(net) #it starts Mininet's CLI for interaction with emulated network

    net.stop() #it stops Mininet emulator after "exit" command entered in Mininet's CLI

'''Parse command-line arguments and kickstart data center's deployment'''
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Emulate fat-tree topology in Mininet with configurable link parameters.') #Argument parser for CLI parameters
    parser.add_argument('-k', type=int, default=4, help="Number of topology's herds and number of ports for each switch. Default is 4.")
    
    #Parameters for core-aggregation links
    parser.add_argument('--core-agg-bw', type=float, default=1000.00, help='Bandwidth of core-aggregation links [Mbps]. Default is 1000.0 [Mbps].')
    parser.add_argument('--core-agg-loss', type=int, default=0, help='Packet loss percentage of core-aggregation links. Default is 0%.')
    parser.add_argument('--core-agg-delay', type=str, default='0ms', help='Delay of core-aggregation links [s/ms/us]. Default is 0 [ms].')
    parser.add_argument('--core-agg-jitter', type=str, default='0ms', help='Average jitter of core-aggregation links [s/ms/us]. Default is 0 [ms].')
    parser.add_argument('--core-agg-max-queue', type=int, default=1000, help='Maximum queue size of core-aggregation links. Default is 1000.')
    
    #Parameters for aggregation-edge links
    parser.add_argument('--agg-edge-bw', type=float, default=1000.00, help='Bandwidth of aggregation-edge links [Mbps]. Default is 1000.0 [Mbps].')
    parser.add_argument('--agg-edge-loss', type=int, default=0, help='Packet loss percentage of aggregation-edge links. Default is 0%.')
    parser.add_argument('--agg-edge-delay', type=str, default='0ms', help='Delay of aggregation-edge links [s/ms/us]. Default is 0 [ms].')
    parser.add_argument('--agg-edge-jitter', type=str, default='0ms', help='Average jitter of aggregation-edge links [s/ms/us]. Default is 0 [ms].')
    parser.add_argument('--agg-edge-max-queue', type=int, default=1000, help='Maximum queue size of aggregation-edge links. Default is 1000.')
    
    #Parameters for edge-server links
    parser.add_argument('--edge-server-bw', type=float, default=1000.00, help='Bandwidth of edge-server links [Mbps]. Default is 1000.0 [Mbps].')
    parser.add_argument('--edge-server-loss', type=int, default=0, help='Packet loss percentage of edge-server links. Default is 0%.')
    parser.add_argument('--edge-server-delay', type=str, default='0ms', help='Delay of edge-server links [s/ms/us]. Default is 0 [ms].')
    parser.add_argument('--edge-server-jitter', type=str, default='0ms', help='Average jitter of server-edge links [s/ms/us]. Default is 0 [ms].')
    parser.add_argument('--edge-server-max-queue', type=int, default=1000, help='Maximum queue size of server-edge links. Default is 1000.')
    
    #Option to compute servers' ARP tables statically
    parser.add_argument('--arp', action='store_true', help='Enable static ARP on servers.') #using --arp will set argument to True, otherwise False

    args=parser.parse_args() #parsed arguments
    if args.k<4 or args.k>8 or args.k%2!=0: #validate k (must be even and between 4 and 8)
        print("Error: valid values for k are 4, 6, and 8")
        sys.exit(1)

    #compact link parameters into lists [core-agg, agg-edge, edge-server]
    bw=[args.core_agg_bw, args.agg_edge_bw, args.edge_server_bw] #float[]
    loss=[args.core_agg_loss, args.agg_edge_loss, args.edge_server_loss] #int[]
    delay=[args.core_agg_delay, args.agg_edge_delay, args.edge_server_delay] #str[]
    jitter=[args.core_agg_jitter, args.agg_edge_jitter, args.edge_server_jitter] #str[]
    max_queue=[args.core_agg_max_queue, args.agg_edge_max_queue, args.edge_server_max_queue] #int[]

    setLogLevel('info') #set Mininet verbosity

    #file_paths=["./DataFiles/FlowStatsSendBase.csv"] (benchmark controller)
    #file_paths=["./DataFiles/FlowStatsSendEnhanced.csv", "./DataFiles/DetectedElephants.csv"] (enhanced controller)
    #file_paths=["./DataFiles/FlowStatsSendGreedy.csv", "./DataFiles/DetectedGreedy.csv"] (enhanced controller + greedy heuristic)
    file_paths=["./DataFiles/FlowStatsSendProb.csv", "./DataFiles/DetectedProb.csv"] #(enhanced controller + probabilistic heuristic)
    for path in file_paths: #clean data files at each simulation run
        if os.path.isfile(path):
            os.remove(path) #delete the file

    run_fattree_topology(args.k, bw, loss, delay, jitter, max_queue, args.arp) #Deploy topology and start Mininet emulator
