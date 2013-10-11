from sim.api import *
from sim.basics import *
from collections import defaultdict

'''
Create your RIP router in this file.
'''
class RIPRouter (Entity):
    counter=0
    def __init__(self):
    # A dictionary to keep track of the forwarding table
    # the keys are the destinations
    # the values are dictionaries with neighbors as keys and distances as values
        self.table=defaultdict(dict)

    # A dictionary to keep track of the mapping of port numbers
    # with neighbors as keys and port numbers as values
        self.port_map={}
    # A dictionary to keep track of the minimum distance to each destination
    # with destination as keys and dictionaries as values
    # where the keys are the neighbor and values are the distances
        self.min_table=defaultdict(dict)

    # A boolean to know whether we have to send routing updates to our neighbors
        self.update=False
    

 #A function  to help calculate the minimum distance to each destination in the table
    def min_distance(self):

        for x in self.table.keys():
            if x in self.min_table:
                minimum=self.min_table[x].values()[0]
                key=self.min_table[x].keys()[0]
            else:
                minimum=100
                key=None
            for y in self.table[x].keys():
                if self.table[x][y]<minimum:
                    self.update=True
                    minimum=self.table[x][y]
                    key=y
                    self.min_table[x]={y:minimum}
                elif self.table[x][y]==minimum and minimum < 100:
                    if self.port_map[y] < self.port_map[self.min_table[x].keys()[0]]:
                        self.update=True
                        minimum=self.table[x][y]
                        key=y
                        self.min_table[x]={y:minimum}


    def handle_rx (self, packet, port):
        self.update=False
    # If the packet is a discovery packet, we have to update our tables and port_map
        if isinstance (packet,DiscoveryPacket):
            if packet.is_link_up:
                self.port_map[packet.src]=port
                self.table[packet.src][packet.src]=1
            else:
                self.port_map.pop(packet.src,None)
                for x in self.table.keys():
                    if packet.src in self.table[x]:
                        self.table[x][packet.src]=100
            #min_table if the closest distance is now down
                for x in self.min_table.keys():
                    if self.min_table[x].keys()[0]== packet.src:
                        self.min_table[x][packet.src]=100
            self.min_distance()
            for x in self.port_map.keys():
                if not isinstance(x,HostEntity):
                    packet=RoutingUpdate()
                    for y in self.min_table.keys():
                      if self.min_table[y].keys()[0]!=x and self.min_table[y].values()[0]<100:
                            packet.add_destination(y,self.min_table[y].values()[0])
                    self.send(packet,self.port_map[x])
                    RIPRouter.counter+=1

        elif isinstance (packet,RoutingUpdate):
            if packet.src in self.port_map:
                dest=packet.all_dests()
                for x in self.table.keys():
                    if x!=packet.src and x not in dest:
                        if packet.src in self.table[x]:
                            self.table[x][packet.src]=100
                    elif x!=packet.src and x in dest:
                        self.table[x][packet.src]=1+packet.get_distance(x)
                        dest.remove(x)
                if len(dest)>0:
                    for x in dest:
                        self.table[x][packet.src]=1+packet.get_distance(x)
                        dest.remove(x)
                for y in self.min_table.keys():
                    for z in self.min_table[y].keys():
                        self.min_table[y][z]=self.table[y][z]

                self.min_distance()
                if self.update:
                    for x in self.port_map.keys():
                        if not isinstance(x,HostEntity):
                            packet=RoutingUpdate()
                            for y in self.min_table.keys():
                                if self.min_table[y].keys()[0]!=x and self.min_table[y].values()[0]<100:
                                    packet.add_destination(y,self.min_table[y].values()[0])
                            self.send(packet,self.port_map[x])
                            RIPRouter.counter+=1
        else:
            if packet.dst in self.min_table and self.min_table[packet.dst].values()[0] <100:
                port_number=self.port_map[self.min_table[packet.dst].keys()[0]]
                self.send(packet,port_number)
    def get_counter(cls):
        return cls.counter
    get_counter=classmethod(get_counter)





                 
           
       



