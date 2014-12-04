'''
Created on Aug 24, 2014

@author: nick
'''

import json, time, uuid
from random import randrange
import unittest

from enablething.task import Task
from enablething.jsonschema import ValidationError


       

class Test_Task(unittest.TestCase):
    def setUp(self):
        # Test cases of different Chronicle records
        self.valid_taskresponse = [
                                    {
                                        "command": {
                                            "announce": {}
                                        }
                                    },
                                    {
                                        "board": "Complete"
                                    },
                                    {
                                        "task_id": "a259a650-5379-11e4-916c-0800200c9a66"
                                    },
                                    {
                                        "title": "Blank"
                                    },
                                    {
                                        "chronicle": [
                                            {
                                                "time_ms": 0.1,
                                                "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                                "hop": 1
                                            },
                                            {
                                                "time_ms": 0.2,
                                                "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                                "hop": 2
                                            },
                                            {
                                                "time_ms": 0.5,
                                                "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                                "hop": 3
                                            }
                                        ]
                                    },
                                    {
                                        "to_unit": "a789ada1-edb5-4cfe-b1f9-8584abbf8a2f"
                                    },
                                    {
                                        "from_unit": "3c82ef61-0875-41d3-99ba-101672d79d6b"
                                    },
                                    {
                                        "response": {
                                        }
                                    }
                                ]
    
    def test_init(self):
        unit_id = uuid.uuid4().hex
        destination = uuid.uuid4().hex
        neighbour = uuid.uuid4().hex
        
        # If core properties are missing a ValidationError should be raised
        self.assertRaises(ValidationError, lambda: Task(unit_id))
        
        # Create a new task with core properties (a task_id
        # is not needed as Task should create one if it is missing).
        # This is the minimum set of variables required to create a new task.
        task = Task(unit_id, 
                    from_unit = unit_id, 
                    to_unit = destination, 
                    command = {"announce":{"fallback_ids":[neighbour]}})
        
        self.assertTrue(task.task_id is not None)
        self.assertTrue(task.response == {})
        
        # Create an "existing" task with a task_id
        task_id = uuid.uuid4().hex
        task = Task(unit_id, 
                    task_id = task_id,
                    from_unit = unit_id, 
                    to_unit = destination, 
                    command = {"announce":{"fallback_ids":[neighbour]}})
    
        self.assertTrue(task.task_id == task_id)
      
    def test_add_response(self):
        # Create an "existing" task with a task_id
        # should create a task with this uuid as a reference.
        unit_id = uuid.uuid4().hex
        destination = uuid.uuid4().hex
        neighbour = uuid.uuid4().hex
        task_id = uuid.uuid4().hex
        task = Task(unit_id, 
                    task_id = task_id,
                    from_unit = unit_id, 
                    to_unit = destination, 
                    command = {"announce":{"fallback_ids":[neighbour]}})
    
        self.assertTrue(task.task_id == task_id)
        
        # Try to write over existing task with same task
        # should be accepted as this has no adverse effect.
        task.add_response(task_id = task_id,
                          from_unit = unit_id, 
                          to_unit = destination, 
                          command = {"announce":{"fallback_ids":[neighbour]}})
        
        new_unit_id = uuid.uuid4().hex
        self.assertRaises(ValidationError, lambda: task.add_response(task_id = task_id,
                                                                     from_unit = new_unit_id, 
                                                                     to_unit = destination, 
                                                                     command = {"announce":{"fallback_ids":[neighbour]}}))
        
        # Try to write over existing task with same task
        # should be accepted without raises an exception
        # as this has no adverse effect.
        task.add_response(task_id = task_id,
                          from_unit = unit_id, 
                          to_unit = destination, 
                          command = {"announce":{"fallback_ids":[neighbour]}})
        
        # Try adding only a response should be accepted.
        task.add_response(response = {"this is a response":"yes"})
        self.assertTrue(task.response == {"this is a response":"yes"})

        # Trying to add a response with another mismatching key should raise
        # a ValidationError
        task.add_response(task_id = task_id,
                          from_unit = unit_id, 
                          to_unit = destination, 
                          command = {"announce":{"fallback_ids":[neighbour]}})
        
        self.assertRaises(ValidationError, lambda: task.add_response(command = {"output":{"this is a different command"}}, 
                                                                     response = {"this is a response":"yes"}))
              
    def test_json(self):
        
        unit_id = uuid.uuid4().hex
        destination = uuid.uuid4().hex
        neighbour = uuid.uuid4().hex
        task_id = uuid.uuid4().hex
        
        task = Task(unit_id, 
                    task_id = task_id,
                    from_unit = unit_id, 
                    to_unit = destination, 
                    command = {"announce":{"fallback_ids":[neighbour]}})
        
        json_result = task.json()
        
        self.assertTrue(json_result['from_unit'] == unit_id)
        self.assertTrue(json_result['to_unit'] == destination)
        self.assertTrue(json_result['command'] == {"announce":{"fallback_ids":[neighbour]}})
        self.assertTrue(json_result['response'] == {})
     

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()