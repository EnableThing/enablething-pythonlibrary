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

def create_valid_json_dict():
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

    return valid_json_dict

class Test_Rest(unittest.TestCase):
    def setUp(self):
        # Test cases for valid command and valid response
        self.valid_json_command = create_valid_json_dict()
        self.valid_json_response = create_valid_json_dict()
        self.valid_json_response['response'] = {"response":"yes"}
        
    def test_init(self):
        ip = "127.0.0.1"
        port = 8081
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        rest = RequestHandler(ip, port, unit_id)
        
        self.assertTrue(rest.url == "http://127.0.0.1:8081")
        self.assertTrue(rest.unit_id == unit_id)
    
    def test_post(self):
        ip = "127.0.0.1"
        port = 8081
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        rest = RequestHandler(ip, port, unit_id)

        # Post invalid JSON, exception raised
        self.assertRaises(AssertionError, lambda:rest.post(unit_id, "{"))
            
        # Post valid but nonsense JSON, exception raised
        try:
            rest.post(unit_id, {})
        except HTTPError as e:
            status_code = e.response.status_code
        self.assertTrue(status_code == 500)

        # Post command, response 200
        rest.post(unit_id, self.valid_json_command)
        # Post command again, response err
        try:
            rest.post(unit_id, self.valid_json_command)
        except HTTPError as e:
            status_code = e.response.status_code
        self.assertTrue(status_code == 500)
        
        # Post response, no exception raised.
        rest.post(unit_id, self.valid_json_response)
        
    def test_get(self):
        ip = "127.0.0.1"
        port = 8081
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        rest = RequestHandler(ip, port, unit_id)
        
        valid_json_command = create_valid_json_dict()
        valid_json_response = create_valid_json_dict()
        valid_json_response['response'] = {"response":"yes"}
        
        # Try to get a task that doesn't exist
        # should raise exception
        task_id = uuid.uuid4().hex
        try:
            json_response = rest.get(url = unit_id + "/task/" + task_id)
        except HTTPError as e:
            status_code = e.response.status_code
        self.assertTrue(status_code == 400)
         
        # Post command       
        rest.post(unit_id, self.valid_json_command)       
        task_id = valid_json_command['task_id']
        
        # Try to get a command that exists, 
        # throws an exception because no response
        try:
            json_response = rest.get(url = unit_id + "/task/" + task_id)
        except HTTPError as e:
            status_code = e.response.status_code
        self.assertTrue(status_code == 400)
        
        # Try to get a command with a response
        # No exception thrown.
        rest.post(unit_id, valid_json_response)
        task_id = valid_json_response['task_id']
        json_response = rest.get(url = unit_id + "/task/" + task_id)
        
        self.assertTrue(valid_json_response['task_id']==task_id)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()