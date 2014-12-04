'''
Created on Aug 24, 2014

@author: nick
'''

import json, time, uuid
import logging
from random import randrange
import unittest
import random

import networkx as nx
import matplotlib.pyplot as plt

from enablething import unitcontroller
from enablething import unit_core
from enablething import unit_custom
from enablething.task import Task
from enablething import config
from enablething import jsonschema

from wsgiref.simple_server import make_server
from SocketServer import ThreadingMixIn
import time
import threading

from restlite import restlite
from enablething.thing import RestHandler

from unit import NeighbourUnit
from unit import shortid
# create logger
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
       
def setup_server(units):
    rest_handler = RestHandler()    
    rest_handler.configure(units)
    httpd = make_server('', 8080, restlite.router(rest_handler.routes))

    httpserver = threading.Thread(target=httpd.serve_forever)
    httpserver.setDaemon(True)
    httpserver.start()  


def configure_unit(unit_setup = unit_core.GenericUnit, unit_specific = None, unit_id = None, input_ids = [], update_cycle = 5, description = "Generic unit", neighbours = []):
    if unit_id == None:
        unit_id = uuid.uuid4().hex
    # Load GUID list from configuration in GUID list
    unit_config = {
                        "common": {
                            "configurable": {
                                "neighbours" : neighbours,
                                "fallback_UUIDs": [],
                                "input_UUIDs": input_ids,
                                "memory_UUID": "g",
                                "taskboard_id": "t",
                                "forecaster_id": "h",
                                "fail_to": "6",
                                "update_cycle": update_cycle,
                                "location": "i",
                                "security": "off",
                                "communication": {
                                    "type": "REST",
                                    "address": ["j","k"]
                                    }
                                },                      
                            "non_configurable": {
                                "unit_id": unit_id,
                                "description": description,
                                "function": "display",
                                "status": "ready",
                                "last_error": "OK",
                                "method" : str(unit_setup)
                                }
                            },
                         "unit_specific": {
                                "configurable": {},
                                "non_configurable": {}
                            
                        }
                    }
  
    if unit_specific == None:
        pass
    else:
        unit_config['unit_specific'] = unit_specific
  
    return unit_setup(id, unit_config)



def test_response_chain():
    
    possible_commands = ({"output":{}}
                         )
    
    
    nodea_id = uuid.uuid4().hex
    nodeb_id = uuid.uuid4().hex
    nodec_id = uuid.uuid4().hex
    noded_id = uuid.uuid4().hex
    nodee_id = uuid.uuid4().hex
    nodef_id = uuid.uuid4().hex
    nodeg_id = uuid.uuid4().hex

    node_a = configure_unit(unit_id = nodea_id, 
                               unit_setup = unit_core.RandomUnit, 
                               input_ids = [], 
                               update_cycle = 0, 
                               description = "Random unit", 
                               neighbours=[nodeb_id])
    node_b = configure_unit(unit_id =nodeb_id, 
                                 unit_setup = unit_core.PassThruUnit, 
                                 input_ids = [nodea_id], 
                                 update_cycle = 0, 
                                 description = "Pass-through unit",  
                                 neighbours=[nodea_id, nodec_id])
    node_c = configure_unit(unit_id = nodec_id, 
                                 unit_setup = unit_core.PassThruUnit, 
                                 input_ids = [nodeb_id], 
                                 update_cycle = 0, 
                                 description = "Output unit",  
                                 neighbours=[nodeb_id,noded_id])
    
    

    
    node_d = configure_unit(unit_id = noded_id, 
                                 unit_setup = unit_core.PassThruUnit, 
                                 input_ids = [nodec_id], 
                                 update_cycle = 0, 
                                 description = "Empty node",  
                                 neighbours=[nodec_id])
    
    node_e = configure_unit(unit_id = nodee_id, 
                                 unit_setup = unit_core.GenericUnit, 
                                 input_ids = [], 
                                 update_cycle = 0, 
                                 description = "Empty node",  
                                 neighbours=[])
    
    node_f = configure_unit(unit_id = nodef_id, 
                                 unit_setup = unit_core.GenericUnit, 
                                 input_ids = [], 
                                 update_cycle = 0, 
                                 description = "Empty node",  
                                 neighbours=[])
    
    node_g = configure_unit(unit_id = nodeg_id, 
                                 unit_setup = unit_core.GenericUnit, 
                                 input_ids = [], 
                                 update_cycle = 0, 
                                 description = "Empty node",  
                                 neighbours=[])
        
    setup_server([node_a, node_b, node_c, node_d, node_e, node_f, node_g])
    
    #for neighbour in inputunit.router.neighbours:
    #    print neighbour.unit_id
    
    command = random.choice(possible_commands)

    task = Task(node_d.unit_id, 
                    to_unit = random.choice([node_a.unit_id]), 
                    from_unit = node_d.unit_id,
                    command = command)         
    node_d.router.transmit.queue(task)
    
    node_d.taskboard.add_taskset([task])

    starttime =time.time()
    #while (time.time() - starttime) <1:
    for _ in xrange(15):
        print time.time() - starttime


        
#         task = Task(node_a.unit_id, 
#                     to_unit = random.choice([node_b.unit_id,node_c.unit_id,node_d.unit_id,node_e.unit_id,node_f.unit_id,node_g.unit_id]), 
#                     from_unit = node_a.unit_id,
#                     command = {"output":{}}) 

        
#         task = Task(node_a.unit_id, 
#                     to_unit = random.choice([node_a.unit_id,node_c.unit_id,node_d.unit_id,node_e.unit_id,node_f.unit_id,node_g.unit_id]), 
#                     from_unit = node_a.unit_id,
#                     command = {"output":{}}) 
#         node_b.taskboard.add(task)
        
#         task = Task(node_a.unit_id, 
#                     to_unit = random.choice([node_a.unit_id,node_b.unit_id,node_d.unit_id,node_e.unit_id,node_f.unit_id,node_g.unit_id]), 
#                     from_unit = node_a.unit_id,
#                     command = {"output":{}}) 
#         node_c.taskboard.add(task)
        
        
    #for _ in xrange(50):      
        node_a.controller_update()  
        node_b.controller_update()
        node_c.controller_update()
        node_d.controller_update()
        node_e.controller_update()
        node_f.controller_update()
        node_g.controller_update()
        
   
        
        #inputunit.taskboard.debug()
        #print "===INPUTUNIT===", inputunit.unit_id[:4]
        #inputunit.taskboard.debug_tasksets()
        print "NODE A"
        node_a.taskboard.debug()
        node_a.router.received.debug()
        node_a.router.transmit.debug()
        node_a.router.subscriptions.debug()

        print "NODE B"
        node_b.taskboard.debug()
        node_b.router.received.debug()
        node_b.router.transmit.debug()
        node_b.router.subscriptions.debug()      

        print "NODE C"
        node_c.taskboard.debug()
        node_c.router.received.debug()
        node_c.router.transmit.debug()
        node_c.router.subscriptions.debug()  

        print "NODE D"
        node_d.taskboard.debug()
        node_d.router.received.debug()
        node_d.router.transmit.debug()
        node_d.router.subscriptions.debug()    


        node_e.taskboard.debug()
        node_f.taskboard.debug()
        node_g.taskboard.debug()
        
        node_a.router.destination_goodness_table()
        node_b.router.destination_goodness_table()
        node_c.router.destination_goodness_table()
        node_d.router.destination_goodness_table()
        node_e.router.destination_goodness_table()
        node_f.router.destination_goodness_table()
        node_g.router.destination_goodness_table()

#         print "===PROCESSUNIT===", processunit.unit_id[:4]
#         processunit.taskboard.debug_tasksets()
#         processunit.taskboard.debug()
#         processunit.router.destination_goodness_table()
#   
#         print "===OUTPUTUNIT===", outputunit.unit_id[:4]
#         outputunit.taskboard.debug_tasksets()
#         outputunit.taskboard.debug()
#         outputunit.router.destination_goodness_table()
          
    
    print "node_a memory"
    for history in node_a.memory.history:
        print history.time_stamp, history.data
    for input in node_a.inputconnector.inputunits:  
        input.debug()    
    print "node_b memory"   
    for history in node_b.memory.history:
        print history.time_stamp, history.data
    
    for input in node_b.inputconnector.inputunits:  
        input.debug()
        
    print "node_c memory"
    for history in node_c.memory.history:
        print history.time_stamp, history.data
    for input in node_c.inputconnector.inputunits:  
        input.debug()  
    print "node_d memory"
    for history in node_d.memory.history:
        print history.time_stamp, history.data        
    for input in node_d.inputconnector.inputunits:  
        input.debug()
        
def network_simulator():
    G = nx.Graph()
    nodes = []
    node_ids = []
    for _ in xrange(10):
        node_id = uuid.uuid4().hex
        node = configure_unit(unit_id = node_id, 
                               unit_setup = unit_core.RandomUnit, 
                               input_ids = [], 
                               update_cycle = 0, 
                               description = "Simulated unit", 
                               neighbours=[])
        #G.add_node(node.unit_id, unit_id = node.unit_id[:4])
        G.add_node(node, unit_id = node.unit_id[:4])
        nodes.append(node)
        node_ids.append(node.unit_id)
    
    # Assign random neighbours to each node
    neighbour_dict ={}
    for node in nodes:
        ip = "127.0.0.1"
        port = 8080
        
        for _ in xrange(2):

            random_neighbour = random.choice(nodes)
            
            node.router.add_neighbour(ip, port, random_neighbour.unit_id)
            random_neighbour.router.add_neighbour(ip, port, node.unit_id)

            G.add_edge(node, random_neighbour)
            
        neighbour_list = []    
        for neighbour in node.router.neighbours:
            print neighbour.unit_id, node.unit_id
            assert(neighbour.unit_id != node.unit_id)
            neighbour_list.append(neighbour.unit_id)
        neighbour_dict[node.unit_id] = neighbour_list
        
    setup_server(nodes)
    

    num_tasks = 0

    starttime =time.time()
    
    
    while (time.time() - starttime) < 90:  
        
        allowable_commands = [{"output":{}}, {"output":{}}]
        #allowable_commands = ({"announce":{}},
        #                      {"announce":{}}
        #                      )
        
        
        from_unit = random.choice(nodes)
        
        allowable_nodes= []

        
        for node in nodes:
            if node.unit_id == from_unit.unit_id:
                pass
            else:
                print node.unit_id, node.unit_id not in neighbour_dict[from_unit.unit_id]
                if node.unit_id not in neighbour_dict[from_unit.unit_id]:
                    allowable_nodes.append(node)
        
        to_unit = random.choice(allowable_nodes)
                    
        num_tasks = num_tasks +1
        task = Task(from_unit.unit_id, 
                    to_unit = to_unit.unit_id, 
                    from_unit = from_unit.unit_id,
                    command = random.choice(allowable_commands))   
   
        assert(from_unit.unit_id != to_unit.unit_id)
        
        from_unit.taskboard.queue(task)              
        #from_unit.router.transmit.queue(task)
        #from_unit.taskboard.add_taskset([task])  
        
        #node = random.choice(nodes)
        #node._new()
        
        for node in nodes:      
            node.controller_update()  
    
    # Simulation complete
    # Assess effeciency
    tasks = []
    failed = 0
    success = 0
    for node in nodes:
        node.taskboard.debug(onlyerrors = True)
        for task in node.taskboard.removed_tasks:
            command = task.command.keys()[0]
            #print command
            
            if command == 'output' and node.unit_id == task.from_unit:
                if task.isResponse() == False:
                    failed = failed + 1
                if task.isResponse() == True:
                    success = success +1
                    task.debug()
                tasks.append(task)
        
        node.taskboard.debug()        
        node.router.destination_goodness_table()
    #for node in nodes:
    #    node.taskboard.debug()
    print "tasks created", num_tasks
    print "success", success
    print "failed", failed
    
    print G.nodes()
    print G.edges()
    
    
    labels=dict((n,d['unit_id']) for n,d in G.nodes(data=True))
    print labels
    nx.draw(G, with_labels = True, node_color='white', labels=labels, node_size =1000)
    #nx.draw_networkx_labels(G, labels=labels)
    plt.show()
            
#test_response_chain()
network_simulator()