'''
Created on Aug 24, 2014

@author: nick
'''

import json, time, uuid
import logging
from random import randrange
import unittest

from .. import unit
from .. import unit_custom
from .. import taskboard_interface
from .. import taskobj
from .. import configmanage
from .. import jsonschema

# create logger
logging.basicConfig(filename='log.log',level=logging.DEBUG)
       

def configure_unit(unit_setup = unit.GenericUnit, unit_specific = None, id = None, input_ids = [], update_cycle = 5, description = "Generic unit"):
    if id == None:
        id = uuid.uuid4().hex
    # Load GUID list from configuration in GUID list
    unit_config = {
                        "common": {
                            "configurable": {
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
                                "last_error": "OK"
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
  
    return unit_setup(unit_config)



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

    #unittest.skip("Skip")
    def test_response_chain(self):
        inputunit = configure_unit(unit_setup = unit.ClockUnit, input_ids = [], update_cycle = 0, description = "Clock unit")
        processunit = configure_unit(unit_setup = unit.PassThruUnit, input_ids = [inputunit.id], update_cycle = 0, description = "Pass-through unit")
        outputunit = configure_unit(unit_setup = unit_custom.charOutputUnit, input_ids = [processunit.id], update_cycle = 0, description = "Output unit")

        for __ in xrange(10):
            inputunit.get_task()
            processunit.get_task()
            outputunit.get_task()
                          
        self.assertTrue('time' in outputunit.memory.history[0].data)    

    def test_SimpleForecastUnit(self):
        inputunit = configure_unit(unit_setup = unit.GenericUnit, input_ids = [], update_cycle = 0, description = "Input unit - clock")
        print "INPUTUNIT.ID", inputunit.id
        processunit = configure_unit(unit_setup = unit.SimpleForecastUnit, input_ids = [inputunit.id], update_cycle = 0, description = "PassThruUnit unit")
        print "PROCESSUNIT.ID", processunit.id
        # Process announces

        for __ in xrange(10):
            inputunit.get_task()
            processunit.get_task()
        
        for i in processunit.memory.forecast:
            print i.time_stamp,i.data
        print "test", processunit.memory.forecast[3].data
        # Should be no memory initially on inputunit       
        self.assertTrue('dummy_reading' in processunit.memory.forecast[3].data)
 
        
    @unittest.skip("Skip")
    def test_weatherInputUnit(self):
        unit_specific =  {
                          "configurable": {
                                           "url": "http://api.wunderground.com/api/",
                                           "key": "PASSWORD",
                                           "feature": "conditions",
                                           "query": "CYVR",
                                           },
                          "non_configurable": {}              
                          }
        weatherunit = configure_unit(unit_setup = unit_custom.weatherInputUnit, unit_specific = unit_specific, input_ids = [], update_cycle = 0, description = "Input unit - weather")
        for __ in xrange(10):
            weatherunit.get_task()
        self.assertTrue('temp_c' in weatherunit.memory.history[0].data)
        

    def test_PassThruUnit(self):
        inputunit = configure_unit(unit_setup = unit.GenericUnit, input_ids = [], update_cycle = 0, description = "Input unit - clock")
        processunit = configure_unit(unit_setup = unit.PassThruUnit, input_ids = [inputunit.id], update_cycle = 0, description = "PassThruUnit unit")        
        # Process announces
        for __ in xrange(5):
            inputunit.get_task()
            processunit.get_task()
            
        # Should be no memory initially on inputunit       
        self.assertTrue('dummy_reading' in inputunit.memory.history[0].data)
        self.assertTrue('dummy_reading' in processunit.memory.history[0].data)
        self.assertTrue('dummy_reading' in processunit.inputboard.input_container[0].history[0].data)

        
    #unittest.skip("Skip")        
    def test_charOutputUnit(self):
        # Setup a clock unit and request the time
        display_unit = configure_unit(unit_setup = unit_custom.charOutputUnit)    
        # Process announce
        rtn = display_unit.display_interface("ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOP")          
        self.assertEqual(rtn, "ABCDEFGHIJKLMNOP/nQRSTUVWXYZABCDEF")   
         
    #unittest.skip("Skip")
    def test_ClockUnit(self):
        # Setup a clock unit and request the time       
        clock_unit = configure_unit(unit_setup = unit.ClockUnit, description = "Clock unit", update_cycle = 0)
        # Process announce
        clock_unit.get_task()
                
        masterunit_id = uuid.uuid4().hex
        masterunit = configure_unit(unit_setup = unit.GenericUnit, id = masterunit_id, input_ids = [clock_unit.id], description = "Master unit", update_cycle = 60)
        
        for __ in xrange(5):
            masterunit.get_task()
            clock_unit.get_task()
        
        self.assertTrue('time' in clock_unit.memory.history[0].data)


        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()