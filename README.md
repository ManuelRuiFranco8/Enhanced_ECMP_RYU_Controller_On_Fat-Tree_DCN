# VM Environment Set-Up:
- Ubuntu 20.04
- Python 3.8.10
- Ryu 4.34
- Mininet 2.3.1
- Open vSwitch 2.13.8


# Codes Explained:

*fatTreeTopo.py* extends Mininet *Topo* class defining a fat-tree topology with configurable port density *k* and link parameters (using TC).

*RyuECMPController.py* runs a benchmark Ryu controller on *localhost:6653* which:
- reads its own configuration from a .txt file;
- keeps track of the Mininet-emulated network in a NetworkX graph ttribute;
- monitors link state in real-time, saving current link state in a Pandas dataframe and exporting it in a .csv file;
- provides proactive ECMP routing ("Equal Cost MultiPath") with hash-based path selection for unicast ARP/IPv4 traffic in the topology;
- provides proactive fat-tree-specific routing for broadcast IPv4 traffic in the topology;
- registers all operations in a .txt file;

*RyuEnhancedECMPController.py* runs an ehanced Ryu controller on *localhost:6653* which:
- reads its own configuration from a .txt file;
- keeps track of the Mininet-emulated network in a NetworkX graph attribute;
- monitors link state in real-time, saving current link state in a Pandas dataframe and exporting it in a .csv file;
- defines a REST endpoint so that current link state may be retrieved in JSON format with an HTTP GET request;
- provides default proactive ECMP routing ("Equal Cost MultiPath") with hash-based path selection for unicast ARP/IPv4 traffic in the topology;
- provides proactive fat-tree-specific routing for broadcast IPv4 traffic in the topology;
- provides ad-hoc elephant flow routing with a VLB-like multipath approach ("Valiant Load-Balancing"); 
- registers all operations in a .txt file;

*DetectElephant.py* monitors all packets transmitted by a Mininet-emulated host by sniffing on host's L2 interface using Scapy. When an elephant flow is detected, an in-band notification is transmitted.
Discovered elephant flows are saved in a Pandas dataframe and exported in a .csv file.

*dataCenter.py* does as follows:
- writes configurations for the controller in a .txt file;
- emulates network with Mininet by deploying a fat-tree topology object;
- performs reachability test between hosts in the topology issuing ping commands;
- starts broadcast/unicast IPv4 traffic on network's hosts issuing hping3 commands;
- runs a thread that periodically fetches link state from controller with an HTTP GET and runs an heuristic to intelligently decide which switches turn off/on to save energy and avoid congestion. All operations are recorded in a .tx file;

*FlowResults.py* takes .csv file written by *DetectElephant.py* and computes stats about elephant flows detection, saving them in a .txt file.

*LinkResults.py* takes .csv file written by controller code and computes new aggregate statistics, saving them in a .csv file.

*MeanStatsPlots.py* and *MeanStatsPlotsHeuristics.py* take the .csv files generated by *LinkResults.py* in multiple iterations (each iteration is a simulation), computing mean stats of all simulations and plotting them using Matplotlib.

# How to run a simulation:
1) Download all the codes in you VM environment;
2) Set all correct paths for the .csv and .txt files in your VM environment;
3) Run *dataCenter.py* from terminal with the command **sudo python3 dataCenter.py -k=[int] --core-agg-bw=[float] --core-agg-loss=[int] --core-agg-delay=[str] --core-agg-jitter=[str] --core-agg-max-queue=[int] --agg-edge-bw=[float] --agg-edge-loss=[int]  --agg-edge-delay=[str] --agg-edge-jitter=[str]  --agg-edge-max-queue=[int] --edge-server-bw=[float] --edge-server-loss=[int]  --edge-server-delay=[str] --edge-server-jitter=[str]  --edge-server-max-queue=[int] --arp (optional)**;
4) Run Ryu controller from another terminal, either with command **ryu-manager RyuECMPController.py** (benchmark controller) or with command **ryu-manager RyuEnhancedECMPController.py** (enhanced controller);

# Debugging:
If you get error **ImportError: cannot import name 'poll' from 'select' (unknown location)** when running Ryu controller’s code, here’s the fix:
1) Open file */usr/local/lib/python3.8/dist-packages/mininet/util.py*;
1) Comment line **from select import poll, POLLIN, POLLHUP**;
2) Add line **from select import \***;

To test basic broadcast functionality, you need to enable ECHO REPLY to broadcast ping messages on Mininet hosts. To do this:
1) Open file */etc/sysctl.conf*;
2) Add line **net.ipv4.icmp_echo_ignore_broadcasts=0**;
3) Execute **sudo sysctl -p** from command line to apply configuration changes. This line is to be executed on each Mininet host after its deployment;

# Credits
This project has been realized as assignment for the course of Smart and Programmable Networks, A.A. 2023-2024


Co-authored by Alessandro D'Amico <alessandro99damico@gmail.com>


Master Degree in Telecommunication Engineering: Computing, Smart Sensing, and Networking


DIMES (Dipartimento di Ingegneria Informatica, Modellistica, Elettronica e Sistemistica)


UNICAL (Università della Calabria)
