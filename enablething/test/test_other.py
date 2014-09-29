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
             
    #unittest.skip("Skip polling test")    
    def test_poll_start(self):
        poll = unit.Poll(5)

        # Should be false when started.
        self.assertFalse(poll.isTrigger())
    #unittest.skip("Skip poll trigger test")     
    def test_poll_trigger(self):
        poll = unit.Poll(5)
        # Should be false when started.       
        time.sleep(7)
        self.assertTrue(poll.isTrigger())

    #unittest.skip("Skip poll not triggered test")
    def test_poll_nottrigger(self):
        poll = unit.Poll(5)
        # Should be false when started.       
        time.sleep(2)
        self.assertFalse(poll.isTrigger())
       

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()