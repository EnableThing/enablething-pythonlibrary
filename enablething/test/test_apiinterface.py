'''
Created on Aug 24, 2014

@author: nick
'''

import json, time, uuid
import logging
import requests
from random import randrange
import unittest

from .. import unit
from .. import unit_custom
from .. import taskboard_interface
from .. import configmanage
from .. import jsonschema
from .. import taskobj
from .. import taskboardobj

from .. import apiinterface

# create logger
logging.basicConfig(filename='log.log',level=logging.DEBUG)
       
class Test_APIInterface(unittest.TestCase):

    def test_createinterface(self):

        validjson =     {
        "title": "Blank", 
        "task_id": "13679ad853f64e6a889e41ed54ffb87c", 
        "chronicle": [
            {
                "time_ms": 0.0, 
                "unit_id": "09df88731b5c47409274c9e1ae4373d5", 
                "hop": 1
            }
        ], 
        "board": "Backlog", 
        "from_unit": "39a3eaa057a849859af88dbed7777dc6", 
        "to_unit": "a6c3e3892ca745febc0508e344ad055c", 
        "command": {
            "announce": {}
        }, 
        "response": {}
    }
        
        unit_id = validjson['from_unit']
        
        api = apiinterface.APIInterface("http://127.0.0.1:8080", unit_id)

    def test_command_validjson(self):
      
        validjson =     {
        "title": "Blank", 
        "task_id": "13679ad853f64e6a889e41ed54ffb87c", 
        "chronicle": [
            {
                "time_ms": 0.0, 
                "unit_id": "09df88731b5c47409274c9e1ae4373d5", 
                "hop": 1
            }
        ], 
        "board": "Backlog", 
        "from_unit": "39a3eaa057a849859af88dbed7777dc6", 
        "to_unit": "a6c3e3892ca745febc0508e344ad055c", 
        "command": {
            "announce": {}
        }, 
        "response": {}
    }
        unit_id = "caf01485-3bb1-4337-a023-5ffc03bf073b"
        print "unit_id", unit_id
        task = taskobj.Task(unit_id, **validjson)
        print "task",task
        #unit_id = task.unit_id
        api = apiinterface.APIInterface("http://127.0.0.1:8080", unit_id)        
        api.task_command(task)

        self.assertEquals(api.response.status_code, 200)
        
        valid_response_json =     {
        "title": "Blank", 
        "task_id": "13679ad853f64e6a889e41ed54ffb87c", 
        "chronicle": [
            {
                "time_ms": 0.0, 
                "unit_id": "09df88731b5c47409274c9e1ae4373d5", 
                "hop": 1
            }
        ], 
        "board": "Backlog", 
        "from_unit": "39a3eaa057a849859af88dbed7777dc6", 
        "to_unit": "a6c3e3892ca745febc0508e344ad055c", 
        "command": {
            "announce": {}
        }, 
        "response": {"valid":3}
    }
        task = taskobj.Task(unit_id, **valid_response_json)
        api.task_response(task)
        
        self.assertEquals(api.response.status_code, 200)      

    def test_getnewtasks(self):
        task_id = uuid.uuid4().hex
        validjson =     {
        "title": "Blank", 
        "task_id": task_id, 
        "chronicle": [
            {
                "time_ms": 0.0, 
                "unit_id": "09df88731b5c47409274c9e1ae4373d5", 
                "hop": 1
            }
        ], 
        "board": "Backlog", 
        "from_unit": uuid.uuid4().hex, 
        "to_unit": uuid.uuid4().hex, 
        "command": {
            "announce": {}
        }, 
        "response": {}
    }
        unit_id = "caf01485-3bb1-4337-a023-5ffc03bf073b"
        print "unit_id", unit_id
        task = taskobj.Task(unit_id, **validjson)
        print "task",task
        #unit_id = task.unit_id
        api = apiinterface.APIInterface("http://127.0.0.1:8080", unit_id)        
        api.task_command(task)

        self.assertEquals(api.response.status_code, 200)
        
        # At this point we have a "backlog" task on the noticeboard
        # Attempt to get it back via a filter.
        
        api.get_new_tasks(unit_id)
        self.assertEquals(api.response.status_code, 200)         

    def test_gettask(self):
        
        unit_id = "caf01485-3bb1-4337-a023-5ffc03bf073b"
        api = apiinterface.APIInterface("http://127.0.0.1:8080", unit_id)        
        #api.get_task(task_id = uuid.uuid4().hex)
        # No task, so error should be raised.
        self.assertRaises(requests.HTTPError, lambda: api.get_task(task_id = uuid.uuid4().hex))
        
        # Create a task without a Response and try to retreive it.
        # Should fail 
        
        task_id = uuid.uuid4().hex
        validjson =     {
        "title": "Blank", 
        "task_id": task_id, 
        "chronicle": [
            {
                "time_ms": 0.0, 
                "unit_id": "09df88731b5c47409274c9e1ae4373d5", 
                "hop": 1
            }
        ], 
        "board": "Backlog", 
        "from_unit": uuid.uuid4().hex, 
        "to_unit": uuid.uuid4().hex, 
        "command": {
            "announce": {}
        }, 
        "response": {}
    }
        task = taskobj.Task(unit_id, **validjson)

        #api.get_task(task_id)
        self.assertRaises(requests.HTTPError, lambda: api.get_task(task_id))
        
        # Create a task with a Response and try to retreive it.
        # Should succeed 
        
        task_id = uuid.uuid4().hex
        
        validjson =     {
        "title": "Blank", 
        "task_id": task_id, 
        "chronicle": [
            {
                "time_ms": 0.0, 
                "unit_id": "09df88731b5c47409274c9e1ae4373d5", 
                "hop": 1
            }
        ], 
        "board": "Backlog", 
        "from_unit": uuid.uuid4().hex, 
        "to_unit": uuid.uuid4().hex, 
        "command": {
            "announce": {}
        }, 
        "response": {"this is a response":1}
    }
        task = taskobj.Task(unit_id, **validjson)                  
        api.task_command(task)
        api.get_task(task_id)      
        
        self.assertEquals(api.response.status_code, 200)    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()