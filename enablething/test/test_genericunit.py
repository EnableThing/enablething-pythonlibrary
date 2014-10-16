'''
Created on Aug 24, 2014

@author: nick
'''

import json, time, uuid
import logging
from random import randrange
import unittest

from enablething import unit_core
from enablething import unit_custom

from enablething import config
from enablething import jsonschema

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



class Test_Taskboard(unittest.TestCase):
             
# Instatiate MemoryUnit and write memory
# Read memory from MemoryUnit

# Check fail conditions - task board for a response to a specific task (Listen for task_id)

# Check success condition - task board for a response to a specific task (Listen for task_id)
# 
# AND unit- Instantiate and perform AND function with 2 inputs and 5 inputs
# OR unit- Instantiate and perform AND function with 2 inputs and 5 inputs
# NOT unit- Instantiate and perform AND function with 1 input
# XOR unit- Instantiate and perform AND function with 2 inputs and 5 inputs
 

    def test_update_configuration(self):

        c = config.ThingConfiguration()
        unit_config = c.units[0].unit_config




        # Test that an attempt to add an acceptable patch passes
        expected_value = randrange(10000)
        
        patch1 = {"common": {
                         "configurable": {"update_cycle": 99999},                                                                      
                        "non_configurable": {"description": "Output unit"}
                        }
                }
        unit_config = c.units[0].patch(patch1)        
        self.assertEquals(unit_config['common']['configurable']['update_cycle'], 99999)
        self.assertEquals(unit_config['common']['non_configurable']['description'], "Output unit")
        
        # Test that an exception is raised when patching incorrectly
        fail_patch = {"common": {"configurable":{"undefined_key_is_bad": 9}}}
        self.assertRaises(jsonschema.ValidationError, lambda: c.units[0].patch(fail_patch))
        
        c = config.ThingConfiguration()
        unit_config = c.units[0].unit_config
        
        # Test that an attempt to add an additional field to unit_specific passes
        expected_value = randrange(10000)
        success_patch = {"unit_specific": {"configurable":{"this field is allowed": expected_value}}}
        unit_config = c.units[0].patch(success_patch)
        self.assertEquals(unit_config['unit_specific']['configurable']['this field is allowed'], expected_value)
        
        # Test that an attempt to add an additional field to unit_specific passes
        expected_value = randrange(10000)
        success_patch = {"unit_specific": {"non_configurable":{"this field is allowed": expected_value}}}
        unit_config = c.units[0].patch(success_patch)
        self.assertEquals(unit_config['unit_specific']['non_configurable']['this field is allowed'], expected_value)
              
    #unittest.skip("Skip clock")        
    def test_process(self):
        test_unit = configure_unit(unit_setup = unit_core.GenericUnit, id = uuid.uuid4().hex, update_cycle = 0)
        for __ in xrange(10):
            test_unit.update()
        self.assertTrue('forecast' in test_unit.memory.json())
        self.assertTrue('history' in test_unit.memory.json())

    #unittest.skip("Skip clock")
    def test_request_multiple_inputs(self):
        # Create two units
        testunit1_id = uuid.uuid4().hex
        testunit2_id = uuid.uuid4().hex      
        masterunit_id = uuid.uuid4().hex
        
        testunit1 = configure_unit(unit_setup = unit_core.GenericUnit, id = testunit1_id)
        testunit2 = configure_unit(unit_setup = unit_core.GenericUnit, id = testunit2_id)
        masterunit = configure_unit(unit_setup = unit_core.GenericUnit, id = masterunit_id, input_ids = [testunit1.unit_id,testunit2.unit_id])
                    
        self.assertTrue(masterunit.status == "new")

        # Instantiate new_unit depending on unit_class
        masterunit.update()
                
        # This should trigger an "announce" and change status to "ready"      
        self.assertTrue(masterunit.status == "ready")
        
        # This should trigger two requests for input, one to each input unit                              
        masterunit.request_inputs()
        
        tasks = []
        for task in masterunit.taskboard.tasks:
            tasks.append(task)
        
        for __ in xrange(5):      
            testunit1.update()
            testunit2.update()
            masterunit.update()
        
        print masterunit.taskboard.debug()
        
        #self.assertTrue(len(tasks)==2)
        
        for task in masterunit.taskboard.tasks:
            print "task.response", task.response
            #response = taskboard_interface.update(task.task_id)
            self.assertNotEqual(task.response, "{}")
        #self.assertTrue(False)
              
            
    
    #unittest.skip("Skip clock")
    def test_announce(self):                         
        # Instantiate new_unit depending on unit_class
        neighbour = uuid.uuid4().hex
        testunit = configure_unit(unit_setup = unit_core.GenericUnit, neighbours = [neighbour])
        # Run unit ... which should generate an "announce"
        for __ in xrange(5):
            testunit.update()
        
        testunit.taskboard.debug()
        task = testunit.taskboard.tasks[0]

        self.assertTrue('announce' in task.command)
        self.assertTrue(neighbour in task.to_unit)


        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()