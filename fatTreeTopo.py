#!/usr/bin/python3

#################################################################################################################Imports
from mininet.topo import Topo #to create the topology object to deploy
from mininet.node import OVSKernelSwitch #to specify the type of switch devices to emulate
from mininet.link import TCLink #to set link's L2 interface parameters

###########################################################################################################FatTree Class
class FatTree(Topo): #it extends mininet.Topo class to define our data center's topology

    ####################################################################################################Class attributes
    __LAYER_CORE=0 #core layer int index
    __LAYER_AGG=1 #aggregation layer int index
    __LAYER_EDGE=2 #edge layer int index
    __LAYER_SERVER=3 #host layer int index
    __BASE_IP=(10, 0, 0, 0) #Base IPv4 address for the data center (network address is 10.0.0.0/24)
    __BASE_herdS=(1, 17, 33, 49, 65, 81, 97, 113) #__BASE_herdS[i]=4th octet value for the first server (leftmost) in herd i

    #######################################################################################################Class methods
    '''Getter method for private class attribute
       @param FatTree class
       @return int FatTree.__LAYER_CORE'''
    @classmethod
    def core_layer(cls):
        return cls.__LAYER_CORE

    '''Getter method for private class attribute
       @param FatTree class
       @return int FatTree.__LAYER_AGG'''
    @classmethod
    def agg_layer(cls):
        return cls.__LAYER_AGG

    '''Getter method for private class attribute
       @param FatTree class
       @return int FatTree.__LAYER_EDGE'''
    @classmethod
    def edge_layer(cls):
        return cls.__LAYER_EDGE

    '''Getter method for private class attribute
       @param FatTree class
       @return int FatTree.__LAYER_SERVER'''
    @classmethod
    def server_layer(cls):
        return cls.__LAYER_SERVER

    #############################################################################################Topology Initialization
    '''Creates FatTree instance, initializing instance attributes
       @param FatTree object
       @param int k  
       @param float[] bw
       @param int[] loss
       @param str[] delay
       @param str[] jitter
       @param int[] max_queue'''
    def __init__(self, k, bw, loss, delay, jitter, max_queue):
        super(FatTree, self).__init__() #constructor of class mininet.Topo

        self.__k=k #number of L2 ports for each switch in the topology
        self.__broadcastAddress="10.0.0.255" #data center network broadcast IPv4 address
        
        #link parameters
        self.__bw=bw #links' bandwidth in Mbps [core-agg, agg-edge, edge-server]
        self.__loss=loss #links' loss percentage [core-agg, agg-edge, edge-server]
        self.__delay=delay #links' delay in seconds [core-agg, agg-edge, edge-server]
        self.__jitter=jitter #link's jitter in seconds [core-agg, agg-edge, edge-server]
        self.__max_queue=max_queue #link's maximum queueing length at L2 ports [core-agg, agg-edge, edge-server]

        #following attributes are populated in the create_topology() function
        self.__coreSw=[] #str[] (list of all core switches in the topology)
        self.__aggSw=[] #str[] (list of all aggregation switches in the topology)
        self.__edgeSw=[] #str[] (list of all edge switches in the topology)
        self.__serverList=[] #str[] (list of all servers in the topology)
        self.__dpid_sw={} #dictionary <str dpid: str switch_name>
        self.__mac_server={} #dictionary <str MAC: str server_name>

        self.__create_topology() #private method adding hosts, switches, and links to topology object

    '''Constructs FatTree topology. Procedure:
           1) Add (k^2)/4 core switches to topology;
           2) Construct herds one by one:
              2.1) Add k/2 aggregation switches to the current herd;
              2.2) Add k/2 edge switches to the current herd:
                   2.2.1) Add k/2 servers (host devices) for each edge switch;
                   2.2.2) Connect servers to the current edge switch;
                   2.2.3) Connect the current edge switch to all aggregation switches of current the herd;
              2.3) Connect current herd's aggregation switches to core switches;
       Connection between aggregation switches and core switches: each agg switch in the herd connects to a distinct group of core switches, agg switches of same
       position in different herds connect to the same group of core switches:
           *First aggregation switch in each herd connects to first k/2 core switches;
           *Second aggregation switch in each herd connects to second k/2 core switches;
           ...
           *Last aggregation switch in each herd connects to last k/2 core switches;
       @param FatTree object'''
    def __create_topology(self):
        herds=range(0, self.__k) #herds are indexed 0 to k-1
        core_sws=range(1, (self.__k//2)+1) #subset of core switches connected to a unique group of aggregation switches (indexed 1 to k/2)
        agg_sws=range((self.__k//2), self.__k) #aggregation switches in a herd are indexed k/2 to k-1
        edge_sws=range(0, (self.__k//2)) #edge switches in a herd are indexed 0 to (k/2)-1
        servers=range(2, (self.__k//2)+2) #servers connected to a given edge switch are indexed 2 to (k/2)+1 (hostId=1 cannot be assigned to servers)

        server_port=1 #server's L2 port number towards its edge switch
        ptcp_port=6654 #starting L4 port number to open additional OpenFlow connections on topology's switches (which are OVS kernel switches)

        #1) Add core switches to the topology
        for a in agg_sws: #for all aggregation switches in a herd
            c_index=a-(self.__k//2)+1 #each agg switch in the herd connects to a distinct group of core switches

            for c in core_sws: #for all core switches serving the current aggregation switch
                core_name=self.get_name(self.__k, c_index, c) #core switch's name has herdId=k, swId=position of agg switch in the herd (c_index),
                                                              #hostId=index of core switch in the group (c)
                core_dpid=self.get_dpid(self.__k, c_index, c) #get DPID of current core switch with the same 3-tuple <herdId, swId, hostId>
                self.__dpid_sw[core_dpid]=core_name #add core switch's <dpid, name> entry to dictionary of all switches

                #Add OVS kernel switch to Mininet topology
                core_node=self.addSwitch(name=core_name, cls=OVSKernelSwitch, dpid=core_dpid, protocols='OpenFlow13', listenPort=ptcp_port) #add Switch instance
                self.__coreSw.append(core_node) #add Switch object to list of core switches
                ptcp_port+=1 #progress ptcp port for next switch

        #2) Create herds
        for p in herds: #for every herd
            agg_port=1 #agg switch's starting L2 port towards edge switches

            #2.1) Add aggregation switches to the current herd
            for a in agg_sws: #for all aggregation switches in the current herd
                agg_name=self.get_name(p, a,1) #aggregation switch's name has herdId=p, swId=a, and hostId=1 (fixed)
                agg_dpid=self.get_dpid(p, a,1) #create switch's DPID with the same 3-tuple
                self.__dpid_sw[agg_dpid]=agg_name #add agg switch's <dpid,name> entry to dictionary of all switches

                #Add OVS kernel switch to Mininet topology
                agg_node=self.addSwitch(name=agg_name, cls=OVSKernelSwitch, dpid=agg_dpid, protocols='OpenFlow13',clistenPort=ptcp_port) #add Switch reference
                self.__aggSw.append(agg_node) #add switch object to list of agg switches
                ptcp_port+=1 #progress ptcp port for next switch

            #2.2) Add edge switches to the current herd
            for e in edge_sws: #for every edge switch in the current herd
                edge_port=1 #edge switch's starting L2 port towards servers
                edge_name=self.get_name(p, e,1) #edge switch's name has herdId=p, swId=e, and hostId=1 (fixed)
                edge_dpid=self.get_dpid(p, e,1) #create switch's DPID with the same 3-tuple
                self.__dpid_sw[edge_dpid]=edge_name #add edge switch's <dpid,name> entry to dictionary of all switches

                #Add OVS kernel switch to Mininet topology
                edge_node=self.addSwitch(name=edge_name, cls=OVSKernelSwitch, dpid=edge_dpid, protocols='OpenFlow13', listenPort=ptcp_port) #add Switch reference
                self.__edgeSw.append(edge_node) #add switch object to list of edge switches
                ptcp_port+=1 #progress ptcp port for next switch

                #2.2.1 - 2.2.2) Connect servers to current edge switch
                for s in servers: #for every server (host device) connected to the current edge switch
                    server_name=self.get_name(p, e, s) #server's name has herdId=p, swId=e, and hostId=s (fixed)
                    server_mac=self.get_mac(p, e, s) #get server MAC address using the same 3-tuple
                    server_ip=self.get_ipv4(p, e, s) #get server IPv4 address using the same 3-tuple

                    server_node=self.addHost(name=server_name, mac=server_mac, ip=f'{server_ip}/24') #Add Host reference to Mininet topology
                    self.__mac_server[server_mac]=server_name #add server's <MAC,name> entry to dictionary of all servers
                    self.__serverList.append(server_node) #add host object to list of servers
                    self.addLink(node1=server_node, node2=edge_node, port1=server_port, port2=edge_port, cls=TCLink, bw=self.__bw[self.__LAYER_EDGE],
                                 loss=self.__loss[self.__LAYER_EDGE],delay=self.__delay[self.__LAYER_EDGE], jitter=self.__jitter[self.__LAYER_EDGE],
                                 max_queue_size=self.__max_queue[self.__LAYER_EDGE]) #add server-edge Link object (specifying L2 ports ob both sides)
                    edge_port+=1 #progress edge L2 port for next server

                #2.2.3) Connect current edge switch to current herd's aggregation switches
                for agg_switch in self.__aggSw[p*(self.__k//2):(p+1)*(self.__k//2)]: #for all aggregation switches in the current herd
                    self.addLink(node1=edge_node, node2=agg_switch, port1=edge_port, port2=agg_port, cls=TCLink, bw=self.__bw[self.__LAYER_AGG],
                                 loss=self.__loss[self.__LAYER_AGG], delay=self.__delay[self.__LAYER_AGG], jitter=self.__jitter[self.__LAYER_AGG],
                                 max_queue_size=self.__max_queue[self.__LAYER_AGG]) #add edge-agg Link object (specifying L2 ports on both sides)
                    edge_port+=1 #progress edge L2 port for next aggregation switch

                agg_port+=1 #progress agg L2 port for next edge switch

            #2.3) Connect aggregation switches in herd to core switches
            i=0 #determines a group of core switches, serving all aggregation switches of the same position (i) in each herd
            for agg_switch in self.__aggSw[p*(self.__k//2):(p+1)*(self.__k//2)]: #for all aggregation switches in current herd
                agg_port=(self.__k//2)+1 #initialize aggregation switch's L2 port towards core switches
                for core_switch in self.__coreSw[i*(self.__k//2):(i+1)*(self.__k//2)]:#for all core switches serving the current aggregation switch
                    self.addLink(node1=core_switch, node2=agg_switch, port1=p+1, port2=agg_port, cls=TCLink, bw=self.__bw[self.__LAYER_CORE],
                                 loss=self.__loss[self.__LAYER_CORE], delay=self.__delay[self.__LAYER_CORE], jitter=self.__jitter[self.__LAYER_CORE],
                                 max_queue_size=self.__max_queue[self.__LAYER_CORE]) #add agg-cre Link object (specifying ports on both sides)
                    agg_port+=1 #progress aggregation L2 port for next core switch

                i+=1 #progress to next group of core switches (serving next agg switch in current herd)

    ###################################################################################################Utility Functions
    '''Return the DPID (datapath ID) of a Switch object by specifying either the node's 3-tuple (herdId, swId, hostId) or the node's name
       @param FatTree object
       @param int herd_id (optional)
       @param int sw_id (optional)
       @param int host_id (optional)
       @param str name (optional)
       @return str dpid'''
    def get_dpid(self, herd_id=0, sw_id=0, host_id=0, name=None):
        if name: #if the name param is specified
            assert name in self.__dpid_sw.values(), f"Switch {name} does not exist in the topology" #name must correspond to a switch in the topology
            p, s, h=[int(s) for s in name.split('_')] #the name string has format "herdId_swId_hostId": split the string and convert each part to int
        else:
            p=herd_id
            s=sw_id
            h=host_id
            assert h==1 or p==self.__k, f"Method get_dpid() cannot be called on topology's servers" #host devices are identified by MACs

        #DPID is a decimal integer with either 7 or 8 digits
        if s<10 and h<10:
            digits=f"{p+1}{0}{0}{s}{0}{0}{h}" #string representing DPID's decimal value
        elif s>=10>h: #s>=10 and h<10
            digits=f"{p+1}{0}{s}{0}{0}{h}" #string representing DPID's decimal value
        elif s<10<=h: #s<10 and h>=10
            digits=f"{p+1}{0}{0}{s}{0}{h}" #string representing DPID's decimal value
        else: #s>=10 and h>=10
            digits=f"{p+1}{0}{s}{0}{h}" #string representing DPID's decimal value
        dpid=f"{int(digits):016x}" #string representing DPID's hexadecimal value
        return dpid #returns hexadecimal DPID in string format

    '''Return the name of a Node object by specifying either the node's 3-tuple (herdId, swId, hostId), or the node's DPID (if node is switch), or the node's MAC 
       (if node is host)
       @param FatTree object
       @param int herd_id (optional)
       @param int sw_id (optional)
       @param int host_id (optional)
       @param int/str dpid (optional)
       @param str mac (optional)
       @return str name'''
    def get_name(self, herd_id=0, sw_id=0, host_id=0, dpid=None, mac=None):
        if dpid and isinstance(dpid, str): #if dpid param is specified as hexadecimal string (by Mininet)
            try:
                return self.__dpid_sw[dpid]  #returns node's name as string "herdId_swId_hostId"
            except KeyError: #if dpid not in self.__dpid_sw.keys() (DPID must correspond to a switch in the topology)
                print(f"KeyError: switch '{dpid}' does not exist in the topology")

        if dpid and isinstance(dpid, int): #if DPID is specified as decimal integer value (by Ryu)
            dpid_str=str(dpid) #convert DPID to str
            assert len(dpid_str)==7 or len(dpid_str)==8, f'Wrong number of digits. DPID decimal value must have either 7 o 8 digits'
            if len(dpid_str)==7: #7 digits DPID
                p=int(dpid_str[0]) #first digit (from left) represents herdId+1
                s=int(dpid_str[1:4]) #digits two to four (from left) represent swId
                h=int(dpid_str[4:]) #remaining digits represent hostId
            else: #8 digits DPID
                p=int(dpid_str[:2]) #first two digits (from left) represent herdId+1
                s=int(dpid_str[2:5]) #digits three to five (from left) represent swId
                h=int(dpid_str[5:]) #remaining digits represent hostId
            name=f"{p-1}_{s}_{h}" #assemble node's name
            assert name in self.nodes(), f'Node {name} does not exist in the topology'
            return name #returns node's name as string "herdId_swId_hostId"

        if mac: #if MAC param is specified
            try:
                return self.__mac_server[mac] #returns node's name as string "herdId_swId_hostId"
            except KeyError: #if mac not in self.__mac_server.keys() (MAC must correspond to a server in the topology)
                print(f"KeyError: server '{mac}' does not exist in the topology")

        else:
            return f"{herd_id}_{sw_id}_{host_id}" #if 3-tuple herd_id, sw_id and host_id is specified, it returns node's name as string "herdId_swId_hostId"

    '''Return the herd_id of a node given its name
       @param FatTree object
       @param str name
       @return int herd_id'''
    def get_herd_id(self, name):
        assert name in self.nodes(), f"Node {name} does not exist in the topology" #name must correspond to a node in the topology
        array_name=[int(s) for s in name.split('_')] #name string has format "herdId_swId_hostId": split the string and convert each part to int
        return array_name[0] #first split int corresponds to herd_id

    '''Return the sw_id of a node given its name
       @param FatTree object
       @param str name
       @return int sw_id'''
    def get_sw_id(self, name):
        assert name in self.nodes(), f"Node {name} does not exist in the topology" #name must correspond to a node in the topology
        array_name=[int(s) for s in name.split('_')] #name string has format "herdId_swId_hostId": split the string and convert each part to int
        return array_name[1] #second split int corresponds to sw_id

    '''Return the host_id of a node given its name
       @param FatTree object
       @param str name
       @return int host_id'''
    def get_host_id(self, name):
        assert name in self.nodes(), f"Node {name} does not exist in the topology" #name must correspond to a node in the topology
        array_id=[int(s) for s in name.split('_')] #name string has format "herdId_swId_hostId": split the string and convert each part to int
        return array_id[2] #third split int corresponds to host_id

    '''Return the MAC address of a server (host device) as string given either the node's 3-tuple (herdId, swId, hostId) or node's name
       @param FatTree object
       @param int herd_id (optional)
       @param int sw_id (optional)
       @param int host_id (optional)
       @param str name (optional)
       @return str MAC'''
    def get_mac(self, herd_id=0, sw_id=0, host_id=0, name=None):
        if name: #if name param is specified
            assert name in self.__mac_server.values(), f"Server {name} does not exist in the topology" #name must correspond to a server in the topology
            p,s,h=[int(s) for s in name.split('_')] #name string has format "herdId_swId_hostId": split the string and convert each part to int
        else:
            p=herd_id
            s=sw_id
            h=host_id
            assert h!=1 and p!=self.__k, f"Method get_mac() cannot be called on topology's switches" #switch devices are identified by DPIDs

        #MAC format is 00:00:00:herd_id:sw_id:host:id (herd_id, sw_id, and host_id are converted into hexadecimal format)
        str_p=f"{p:02x}"
        str_s=f"{s:02x}"
        str_h=f"{h:02x}"
        return f"00:00:00:{str_p}:{str_s}:{str_h}" #return server's MAC as string

    '''Return a server's IPv4 address as string given either the node's 3-tuple (herdId, swId, hostId) or node's name
       @param FatTree object
       @param int herd_id (optional)
       @param int sw_id (optional)
       @param int host_id (optional)
       @param str name (optional)
       @return str ip'''
    def get_ipv4(self, herd_id=0, sw_id=0, host_id=0, name=None):
        if name: #if the name param is specified
            assert name in self.__mac_server.values(), f"Server {name} does not exist in the topology" #name must correspond to a server in the topology
            p, s, h=[int(s) for s in name.split('_')] #name string has format "herdId_swId_hostId": split the string and convert each part to int
        else:
            p=herd_id
            s=sw_id
            h=host_id
            assert h!=1 and p!=self.__k, f"Method get_dpid() cannot be called on topology's switches" #switch devices are identified by DPIDs

        ip_address=list(self.__BASE_IP) #assemble IPv4 address of specified server
        ip_address[3]=self.__BASE_herdS[p]+((self.__k//2)*s)+h-2 #integer value of fourth octet of current server's IPv4
        return f"{ip_address[0]}.{ip_address[1]}.{ip_address[2]}.{ip_address[3]}" #return IPv4 address as string

    ####################################################################Functions to navigate the network hierarchically
    '''Return the layer index of a node in the network given its name
       @param FatTree object
       @param str name 
       @return int layer'''    
    def get_layer(self, name):
        if name in self.__coreSw:
            return self.__LAYER_CORE #returns index 0
        if name in self.__aggSw:
            return self.__LAYER_AGG #returns index 1
        if name in self.__edgeSw:
            return self.__LAYER_EDGE #returns index 2
        if name in self.__serverList:
            return self.__LAYER_SERVER #returns index 3
        return -1 #if specified node not found in any layer
        
    '''Return a list of all nodes at a provided layer
       @param FatTree object
       @param int layer
       @return str[] nodeList'''
    def get_layer_nodes(self, layer):
        if layer==self.__LAYER_CORE:
            return self.__coreSw #returns list of core switches
        elif layer==self.__LAYER_AGG:
            return self.__aggSw #returns list of agg switches
        elif layer==self.__LAYER_EDGE:
            return self.__edgeSw #return list of edge switches
        elif layer==self.__LAYER_SERVER:
            return self.__serverList #return list of servers (host devices)
        return [] #if invalid layer specified
        
    '''Return list of node names one layer higher (closer to core) connected to a given node (upward neighbors)
       @param FatTree object
       @param str name
       @return str[] nodeList'''
    def get_up_nodes(self, name):
        assert name in self.nodes(), f"Node {name} does not exist in the topology" #name must correspond to a node in the topology
        layer=self.get_layer(name)-1 #layer index above the specified node
        return [n for n in self.g[name].keys() if self.get_layer(n)==layer] #list of node names (self.g[name] contains all neighbor nodes of node "name")
        
    '''Return list of node names one layer lower (further from core) connected to a given node (downward neighbors)
       @param FatTree object
       @param str name
       @return str[] nodeList'''
    def get_down_nodes(self, name):
        assert name in self.nodes(), f"Node {name} does not exist in the topology" #name must correspond to a node in the topology
        layer=self.get_layer(name)+1 #layer index below the specified node
        return [n for n in self.g[name].keys() if self.get_layer(n)==layer] #list of node names (self.g[name] contains all neighbor nodes of node "name")

    '''Return upward edges (towards upper layer) of a given node
       @param FatTree object
       @param str name
       @return list[(str node_name, str neighbor_name)]'''
    def get_up_edges(self, name):
        assert name in self.nodes(), f"Node {name} does not exist in the topology" #name must correspond to a node in the topology
        node_names=[n for n in self.get_up_nodes(name)] #get list of upward neighbors of specified node
        return [(name, n) for n in node_names] #list of all edges: an edge is a tuple (specified_node,upward_node)

    '''Return downward edges (towards down layer layer) of a given node
       @param FatTree object
       @param str name
       @return list[(str node_name, str neighbor_name)]'''
    def get_down_edges(self, name):
        assert name in self.nodes(), f"Node {name} does not exist in the topology" #name must correspond to a node in the topology
        node_names=[n for n in self.get_down_nodes(name)] #get list of downward neighbors of specified node
        return [(name, n) for n in node_names] #list of all edges: an edge is a tuple (specified_node,downward_node)

    '''Given a pair of source-destination nodes in the topology, it statically computes the output L2 port on the source and the input L2 port on the destination. 
       This is possible because each layer has consistent port mapping rules and because node names have topological significance: L2 ports may be calculated from 
       the names of the source and destination nodes
       @param FatTree object
       @param str src (source node's name)
       @param str dst (destination node's name)
       @return tuple (int src_port, int dst_port>):
            - src_port: L2 port on source node leading to the destination node
            - dst_port: L2 port on destination node leading to the source node'''
    def port(self, src, dst): #overrides mininet.Topo.port() method
        src_layer=self.get_layer(src) #source's layer index
        herd_src, sw_src, host_src=[int(s) for s in src.split('_')] #3-tuple herdId, swId, hostId of source node

        dst_layer=self.get_layer(dst) #destination's layer index
        herd_dst, sw_dst, host_dst=[int(s) for s in dst.split('_')] #3-tuple herdId, swId, hostId of destination node

        if src_layer==self.__LAYER_SERVER and dst_layer==self.__LAYER_EDGE: #server->edge
            src_port=1 #a server (host device) has a single exit port
            dst_port=host_src-1 #ingress port on edge: serverHostId-1
        elif src_layer==self.__LAYER_EDGE and dst_layer==self.__LAYER_SERVER: #server<-edge
            src_port=host_dst-1 #egress port on edge: serverHostId-1
            dst_port=1 #a server has a single enter port
        elif src_layer==self.__LAYER_EDGE and dst_layer==self.__LAYER_AGG: #edge->agg
            src_port=sw_dst+1 #egress port on edge: aggSwId+1
            dst_port=sw_src+1 #ingress port on agg: edgeSwId+1
        elif src_layer==self.__LAYER_AGG and dst_layer==self.__LAYER_EDGE: #edge<-agg
            src_port=sw_dst+1 #egress port on agg: edgeSwId+1
            dst_port=sw_src+1 #ingress port on edge: aggSwId+1
        elif src_layer==self.__LAYER_AGG and dst_layer==self.__LAYER_CORE: #agg->core
            src_port=host_dst+(self.__k//2) #egress port on agg: coreHostId+(k/2)
            dst_port=herd_src+1 #ingress port on core: aggherdId+1
        elif src_layer==self.__LAYER_CORE and dst_layer==self.__LAYER_AGG: #agg<-core
            src_port=herd_dst+1 #egress port on core: aggherdId+1
            dst_port=host_src+(self.__k//2) #ingress port on agg: coreHostId+(k/2)
        else: #if src and dst nodes do not reside on communicating layers, or either node does not exist in the topology
            raise Exception("Could not find port mapping between specified nodes")
        return src_port, dst_port #returns a tuple of port numbers

    #######################################################################################Getter of instance attributes
    '''Return value of attribute __k (number of ports for each switch in the topology)
       @param FatTree self
       @return int k'''
    @property
    def k(self):
        return self.__k

    '''Return value of attribute __bw (bandwidth [Mbps] of links in the topology)
       @param FatTree self
       @return float[] bw'''
    @property
    def bw(self):
        return self.__bw

    '''Return value of attribute __loss (loss percentage of links in the topology)
       @param FatTree self
       @return int[] loss'''
    @property
    def loss(self):
        return self.__loss

    '''Return value of attribute __delay (delay [s/ms/us] of links in the topology)
       @param FatTree self
       @return str[] delay'''
    @property
    def delay(self):
        return self.__delay

    '''Return value of attribute __jitter (jitter [s/ms/us] of links in the topology)
       @param FatTree self
       @return str[] jitter'''
    @property
    def jitter(self):
        return self.__jitter

    '''Return value of attribute __max_queue (max queue size of port 2 interfaces in the topology)
       @param FatTree self
       @return int[] max_queue'''
    @property
    def max_queue(self):
        return self.__max_queue

    '''Return value of attribute __broadcastAddress (broadcast IPv4 addresses for the network)
       @param FatTree self
       @return str broadcastAddress'''
    @property
    def broadcast_address(self):
        return self.__broadcastAddress
