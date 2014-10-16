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

from enablething.task import Task, Chronicle
from enablething import config
from enablething import jsonschema
from enablething.taskboard import Taskboard

# create logger
logging.basicConfig(filename='log.log',level=logging.DEBUG)
       

def configure_unit(unit_setup = unit_core.GenericUnit, unit_specific = None, id = None, input_ids = [], update_cycle = 5, description = "Generic unit"):
    if id == None:
        id = uuid.uuid4().hex
    # Load GUID list from configuration in GUID list
    unit_config = {
                        "common": {
                            "configurable": {
                                "neighbours" : [],
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

    def test_chronicle(self):
            
        # Create a task that requests configuration from input unit
        id0 = uuid.uuid4().hex 
        id1 = uuid.uuid4().hex
        id2 = uuid.uuid4().hex
        taskboard = Taskboard(id1)
        command = {"announce":{}}
        chronicle = [{'time_ms': 0.0, 'unit_id': id0, 'hop': 1}]
                   
        task = Task(unit_id = id0, chronicle = chronicle, from_unit = id1, to_unit = id2, command = command)     
        taskboard.add(task)  
        self.assertTrue(len(task.chronicle)==1)
        
        c = Chronicle(unit_id = id1, chronicle = task.chronicle)
        c.update()
        
        task.chronicle = c.json()      
        self.assertTrue(len(task.chronicle)==2)
        
        c = Chronicle(unit_id = id2, chronicle = task.chronicle)
        c.update()
        
        self.assertTrue(len(task.chronicle)==3)
        
        print "task.chronicle", c.chronicle
         
        # Test last
        self.assertEquals(c.last(), id2)
        # Test next
        self.assertEquals(c.next(id1), id2)
        self.assertEquals(c.next(id0), id1)
        # Test previous
        self.assertEquals(c.previous(id1), id0)
        self.assertEquals(c.previous(id2), id1)
        
        # Test error condition
        
        self.assertRaises(LookupError, lambda: c.next(id2))
        
        self.assertRaises(LookupError, lambda: c.previous(id0))


 
    def test_command_memory(self):
        # Test sending memory and replacing contents of
        # existing memory
        
        # Set update cycle to 10,000 to avoid generating data.
        inputunit = configure_unit(unit_setup = unit_core.GenericUnit, input_ids = [], update_cycle = 0, description = "Test string af31")
        print "INPUTUNIT.unit_id", inputunit.unit_id
        processunit = configure_unit(unit_setup = unit_core.PassThruUnit, input_ids = [inputunit.unit_id], update_cycle = 0, description = "PassThruUnit unit")
        print "PROCESSUNIT.unit_id", processunit.unit_id
        # Process announces
        
        for __ in xrange(5):
            inputunit.update()
            processunit.update()
            
        # Test that empty strings can be sent/
        id = uuid.uuid4().hex
        taskboard = Taskboard(id)
        command = {"memory":
                    {'forecast': [], 
                     'history': []}
                   }
                            
        task = Task(unit_id = processunit.unit_id, from_unit = processunit.unit_id, to_unit = inputunit.unit_id, command = command)
        taskboard.add(task)
        
        for __ in xrange(1):
            inputunit.update()
            processunit.update()

        print "forecast"
        for i in inputunit.memory.forecast:
            print i.data
        print "history"
        for i in inputunit.memory.history:
            print i.data
            
        self.assertRaises(IndexError,lambda: inputunit.memory.forecast[0].data)
        self.assertRaises(IndexError, lambda: inputunit.memory.history[0].data)
            
        ''' Test that array of data points can be sent and received '''     
      
#         print "forecast"
#         for i in inputunit.memory.forecast:
#             print i.data
#         print "history"
#         for i in inputunit.memory.history:
#             print i.data
        
        self.assertRaises(IndexError, lambda: inputunit.memory.history[0].data)
        self.assertRaises(IndexError, lambda: inputunit.memory.forecast[0].data)
        
        command = {"memory":
                    {'forecast': 
                        [{'time_stamp': 'Sat, 27 Sep 2014 23:32:00 -0000', 'data': {'dummy_reading': 707}},
                         {'time_stamp': 'Sat, 27 Sep 2014 23:31:59 -0000', 'data': {'dummy_reading': 808}}, 
                         {'time_stamp': 'Sat, 27 Sep 2014 23:31:57 -0000', 'data': {'dummy_reading': 909}}], 
                     'history': 
                        [{'time_stamp': 'Sat, 27 Sep 2014 23:32:00 -0000', 'data': {'dummy_reading': 404}},
                         {'time_stamp': 'Sat, 27 Sep 2014 23:31:59 -0000', 'data': {'dummy_reading': 505}}, 
                         {'time_stamp': 'Sat, 27 Sep 2014 23:31:57 -0000', 'data': {'dummy_reading': 606}}]}
                   }
        
        task = Task(unit_id = processunit.unit_id, from_unit = processunit.unit_id, to_unit = inputunit.unit_id, command = command)
        taskboard.add(task)
        
        for __ in xrange(1):
            inputunit.update()
            processunit.update()
 
        print "forecast"
        for i in inputunit.memory.forecast:
            print i.data
        print "history"
        for i in inputunit.memory.history:
            print i.data           
        # Should be no memory initially on inputunit       

        self.assertEquals({"dummy_reading":707}, inputunit.memory.forecast[0].data)
        self.assertEquals({"dummy_reading":404}, inputunit.memory.history[0].data)
        
        

    def test_command_configuration(self):
        # Test sending a configuration request, and confirming the unit responds
        # with current configuration.
        inputunit = configure_unit(unit_setup = unit_core.GenericUnit, input_ids = [], update_cycle = 0, description = "Test string af31")
        print "INPUTUNIT.unit_id", inputunit.unit_id
        processunit = configure_unit(unit_setup = unit_core.PassThruUnit, input_ids = [inputunit.unit_id], update_cycle = 0, description = "PassThruUnit unit")
        print "PROCESSUNIT.unit_id", processunit.unit_id
        # Process announces
        
        for __ in xrange(5):
            inputunit.update()
            processunit.update()
            
        # Create a task that requests configuration
        id = uuid.uuid4().hex
        taskboard = Taskboard(id)
        command = {"configuration":"Null"}
                    
        task = Task(unit_id = processunit.unit_id, from_unit = processunit.unit_id, to_unit = inputunit.unit_id, command = command)
        task_id = task.task_id
        taskboard.add(task)
        
        for __ in xrange(5):
            inputunit.update()
            processunit.update()
            
        # Should be no memory initially on inputunit       
        self.assertEquals(inputunit.configuration.unit_config["common"]["non_configurable"]["description"], "Test string af31")

    def test_command_setting(self):
        inputunit = configure_unit(unit_setup = unit_core.GenericUnit, input_ids = [], update_cycle = 0, description = "Input unit - clock")
        print "INPUTUNIT.unit_id", inputunit.unit_id
        processunit = configure_unit(unit_setup = unit_core.PassThruUnit, input_ids = [inputunit.unit_id], update_cycle = 0, description = "PassThruUnit unit")
        print "PROCESSUNIT.unit_id", processunit.unit_id
        # Process announces
        
        for __ in xrange(5):
            inputunit.update()
            processunit.update()
            
        # Create a task that requests configuration from input unit 
        id = uuid.uuid4().hex
        taskboard = Taskboard(id)
        command = {"setting":{"common": {"configurable": {"update_cycle": 9999}}}}                   
        task = Task(unit_id = processunit.unit_id, from_unit = processunit.unit_id, to_unit = inputunit.unit_id, command = command)
        task_id = task.task_id
        taskboard.add(task)
        
        for __ in xrange(5):
            inputunit.update()
            processunit.update()
            
        # Should be no memory initially on inputunit       
        self.assertEquals(inputunit.configuration.unit_config["common"]["configurable"]["update_cycle"], 9999)                
        

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
    def test_command_announce_b(self):
        
                         
        # Instantiate new_unit depending on unit_class
         
        testunit = configure_unit(unit_setup = unit_core.GenericUnit)
        # Run unit ... which should generate an "announce"
        
        testunit.update()
        
        print testunit.taskboard.last_removed_task_id()
        
        task = taskboard_interface.update(testunit.taskboard.last_removed_task_id())
        

        print task['command'], "announce" in task['command']
        self.assertTrue("announce" in task['command'])
        
    def test_command_announce_a(self):
        inputunit = configure_unit(unit_setup = unit_core.GenericUnit, input_ids = [], update_cycle = 0, description = "Input unit - clock")
        print "INPUTUNIT.unit_id", inputunit.unit_id
        processunit = configure_unit(unit_setup = unit_core.PassThruUnit, input_ids = [inputunit.unit_id], update_cycle = 0, description = "PassThruUnit unit")
        print "PROCESSUNIT.unit_id", processunit.unit_id
        # Process announces
        
        for __ in xrange(5):
            inputunit.update()
            processunit.update()
            
        # Create a task that requests configuration from input unit 
        id = uuid.uuid4().hex
        taskboard = Taskboard(id)
        command = {"announce":{}}                
        task = Task(unit_id = processunit.unit_id, from_unit = processunit.unit_id, to_unit = inputunit.unit_id, command = command)
        task_id = task.task_id
        taskboard.add(task)
        
        for __ in xrange(5):
            inputunit.update()
            processunit.update()
            
        print "task.response", task.response
        inputunit.taskboard.debug()
        processunit.taskboard.debug()
            
              
        self.assertTrue(False)
        # Need to figure out how to assess success             

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()