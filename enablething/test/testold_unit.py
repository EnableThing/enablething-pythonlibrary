'''
Created on Aug 24, 2014

@author: nick
'''

import json, time, uuid
from random import randrange
import unittest
from requests.exceptions import HTTPError

from enablething.jsonschema import ValidationError

from rest import RequestHandler
from task import Task
from unit import Unit

def create_valid_task():
    unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
    task_id = uuid.uuid4().hex
    valid_json_dict = {
        "title": "Blank", 
        "task_id": task_id, 
        "chronicle": [
                                        {
                                            "time_ms": 0.3,
                                            "unit_id": unit_id,
                                            "hop": 1
                                        }
                                    ], 
        "from_unit": unit_id, 
        "to_unit": "a789ada1-edb5-4cfe-b1f9-8584abbf8a2f", 
        "command": {
            "announce": {}
        }, 
        "response": {}
    }
    valid_task = Task(unit_id, **valid_json_dict)
    return valid_task   

class Test_Rest(unittest.TestCase):
    def setUp(self):
        # Test cases for valid command and valid response

        self.valid_command = create_valid_task()
        print self.valid_command
        
        self.valid_response = create_valid_task()
        self.valid_response.add_response(response = {"Response":1})                        
                                         
    def test_init(self):
        ip = "127.0.0.1"
        port = 8080
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        testunit = Unit(ip, unit_id, fallback_units = [uuid.uuid4().hex, uuid.uuid4().hex])
        
        self.assertTrue(testunit.rest.url == "http://127.0.0.1:8080")
        self.assertTrue(testunit.unit_id == unit_id)
    
    def test_post_task(self):
        ip = "127.0.0.1"
        port = 8080
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        testunit = Unit(ip, unit_id, fallback_units = [uuid.uuid4().hex, uuid.uuid4().hex])
        
        task = create_valid_task()
        # Posting a task should result in no error
        testunit.post_task(task)
        
        
        # Posting test again should raise an error
        try:
            testunit.post_task(task)
        except HTTPError as e:
            status_code = e.response.status_code
            
        self.assertTrue(status_code == 500)
        
        valid_response = self.valid_response
        testunit.post_task(valid_response)
        
    def get_new_responses(self):
        self.assertTrue(False)

    def test_get_response(self):
        ip = "127.0.0.1"
        port = 8080
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        testunit = Unit(ip, unit_id, fallback_units = [])
        
        valid_command = create_valid_task()
        valid_response = create_valid_task()
        valid_response.add_response(response = {"Response":1})
        
        testunit.post_task(valid_command)
        testunit.post_task(valid_response)
        
        testunit.get_response(valid_command)
                
        
    def test_get_new_commands(self):
        ip = "127.0.0.1"
        port = 8080
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        testunit = Unit(ip, unit_id, fallback_units = [])
        # Post five tasks to taskboard
        for _ in xrange(5):
            task = create_valid_task()
            # Posting a task should result in no error
            testunit.post_task(task)
        tasks = testunit.get_new_commands()
        print tasks
        self.assertTrue(len(tasks) == 5)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()