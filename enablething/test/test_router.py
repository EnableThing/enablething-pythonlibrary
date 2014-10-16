'''
Created on Aug 24, 2014

@author: nick
'''

import json, time, uuid
import logging
from random import randrange
import unittest

from enablething import unit
from enablething import unit_core
from enablething import unit_custom
#from enablething import taskboard_interface
from enablething import config
from enablething import jsonschema
from enablething import router

# create logger
logging.basicConfig(filename='log.log',level=logging.DEBUG)
       

def configure_unit(unit_setup = unit_core.GenericUnit, unit_specific = None, id = None, input_ids = [], update_cycle = 5, description = "Generic unit", neighbours = []):
    if id == None:
        id = uuid.uuid4().hex
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
                                "unit_id": id,
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



class Test_Router(unittest.TestCase):
             
# Instatiate MemoryUnit and write memory
# Read memory from MemoryUnit

# Check fail conditions - task board for a response to a specific task (Listen for task_id)

# Check success condition - task board for a response to a specific task (Listen for task_id)
# 
# AND unit- Instantiate and perform AND function with 2 inputs and 5 inputs
# OR unit- Instantiate and perform AND function with 2 inputs and 5 inputs
# NOT unit- Instantiate and perform AND function with 1 input
# XOR unit- Instantiate and perform AND function with 2 inputs and 5 inputs

    

    def test_neighbour(self):
        # Check that a call to update neighbour creates a neighbour entry
        # and resets timer
        neighbour_table = router.NeighbourTable()
        neighbour1_uuid = uuid.uuid4().hex
        neighbour2_uuid = uuid.uuid4().hex
        neighbour3_uuid = uuid.uuid4().hex
        
        neighbour_table.update(neighbour1_uuid)
        neighbour_table.update(neighbour2_uuid)
        neighbour_table.update(neighbour3_uuid)
        
        time.sleep(.2)
        
        neighbour_table.update(neighbour1_uuid)
        
        neighbour_table.debug()

        self.assertEquals(neighbour_table.last_contact[neighbour1_uuid],0)
        self.assertNotEqual(neighbour_table.last_contact[neighbour2_uuid],0)
        self.assertNotEqual(neighbour_table.last_contact[neighbour3_uuid],0)

    def test_chronicle(self):
        self.assertTrue(False)
        
    def test_pheromone(self):
        self.assertTrue(False)
        
    def test_process_task(self):
        self.assertTrue(False)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()