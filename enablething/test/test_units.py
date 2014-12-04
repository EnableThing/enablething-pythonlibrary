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
from enablething.task import Task
from enablething import config
from enablething import jsonschema

from wsgiref.simple_server import make_server
from SocketServer import ThreadingMixIn
import time
import threading

from restlite import restlite
from enablething.thing import RestHandler

# create logger
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
       
def setup_server(units):
    rest_handler = RestHandler()    
    rest_handler.configure(units)
    print "routes",rest_handler.routes
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


class Test_Taskboard(unittest.TestCase):


      


    #unittest.skip("Skip")
    def test_response_chain(self):
        inputunit_id = uuid.uuid4().hex
        processunit_id = uuid.uuid4().hex
        outputunit_id = uuid.uuid4().hex
        
        inputunit = configure_unit(unit_id = inputunit_id, 
                                   unit_setup = unit_core.ClockUnit, 
                                   input_ids = [], 
                                   update_cycle = 0, 
                                   description = "Clock unit", 
                                   neighbours=[processunit_id, outputunit_id])
        processunit = configure_unit(unit_id =processunit_id, 
                                     unit_setup = unit_core.PassThruUnit, 
                                     input_ids = [inputunit_id], 
                                     update_cycle = 0, 
                                     description = "Pass-through unit",  
                                     neighbours=[inputunit_id, outputunit_id])
        outputunit = configure_unit(unit_id = outputunit_id, 
                                    unit_setup = unit_custom.charOutputUnit, 
                                    input_ids = [processunit_id], 
                                    update_cycle = 0, 
                                    description = "Output unit",  
                                    neighbours=[processunit_id, inputunit_id])
        setup_server([inputunit,processunit, outputunit])
        
                
        for __ in xrange(10):
            inputunit.controller_update()
            processunit.controller_update()
            outputunit.controller_update()
            
        print outputunit.taskboard.debug()
        print "outputunit.memory.history[0].data",outputunit.memory.history[0].data
        self.assertTrue('time' in outputunit.memory.history[0].data)    

    def test_SimpleForecastUnit(self):
        inputunit = configure_unit(unit_setup = unit_core.GenericUnit, input_ids = [], update_cycle = 0, description = "Input unit - clock")
        print "INPUTUNIT.ID", inputunit.unit_id
        processunit = configure_unit(unit_setup = unit_core.SimpleForecastUnit, input_ids = [inputunit.unit_id], update_cycle = 0, description = "PassThruUnit unit")
        print "PROCESSUNIT.ID", processunit.unit_id
        # Process announces

        setup_server([inputunit, processunit])

        for __ in xrange(10):
            inputunit._ready()
            processunit._ready()
        
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
                                           "key": "51e4897db8b4aa29",
                                           "feature": "conditions",
                                           "query": "CYVR",
                                           },
                          "non_configurable": {}              
                          }
        weatherunit = configure_unit(unit_setup = unit_custom.weatherInputUnit, unit_specific = unit_specific, input_ids = [], update_cycle = 0, description = "Input unit - weather")
        for __ in xrange(10):
            weatherunit.update()
            
        self.assertTrue('temp_c' in weatherunit.memory.history[0].data)
        #self.assertTrue(False)
        

    def test_PassThruUnit(self):
        inputunit = configure_unit(unit_setup = unit_core.RandomUnit, input_ids = [], update_cycle = 0, description = "Random unit")
        processunit = configure_unit(unit_setup = unit_core.PassThruUnit, input_ids = [inputunit.unit_id], update_cycle = 0, description = "PassThruUnit unit")        
        
        setup_server([inputunit,processunit])
        # Process announces
        for __ in xrange(10):
            
            inputunit.controller_update()
            processunit.controller_update()
        print "inputunit.taskboard.debug()"
        for task in inputunit.taskboard.tasks:
            print task.task_id, task.command, task.response
        
        print "processunit.taskboard.debug()"
        for task in processunit.taskboard.tasks:
            print task.task_id, task.command, task.response
        
        for history in inputunit.memory.history:
            print history.data
        print inputunit.memory.history[0].data
        print processunit.memory.history[0].data
            
        # Should be no memory initially on inputunit       
        self.assertTrue('dummy_reading' in inputunit.memory.history[0].data)
        self.assertTrue('dummy_reading' in processunit.memory.history[0].data)
        self.assertTrue('dummy_reading' in processunit.inputconnector.inputunits[0].memory.history[0].data)

        
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
        clock_unit = configure_unit(unit_setup = unit_core.ClockUnit, description = "Clock unit", update_cycle = 0)
        # Process announce
    
        for __ in xrange(5):
            clock_unit.controller_update()

        self.assertTrue(len(clock_unit.memory.history)>1)        
        for history in clock_unit.memory.history:
            self.assertTrue('time' in history.data)

    #unittest.skip("Skip")
    def test_RandomUnit(self):
        # Setup a clock unit and request the time       
        clock_unit = configure_unit(unit_setup = unit_core.RandomUnit, description = "Random unit", update_cycle = 0)
        # Process announce
    
        for __ in xrange(5):
            clock_unit.controller_update()

        self.assertTrue(len(clock_unit.memory.history)>1)        
        for history in clock_unit.memory.history:
            print history.data
            self.assertTrue('random_number' in history.data)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()