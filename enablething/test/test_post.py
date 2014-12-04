'''
Created on Aug 24, 2014

@author: nick
'''

import json, time, uuid
from random import randrange
import unittest
from requests.exceptions import HTTPError
import requests

from enablething.jsonschema import ValidationError

import rest


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
        
    def test_posta(self):
        request_url = "http://127.0.0.1:8080/3c82ef61-0875-41d3-99ba-101672d79d6b"
        
        print "request_url", request_url
        
        #data = json.dumps(self.valid_json_command)

        data = {"task_id": "b505c6938abb4a518480ee8b0a1f2af3", "chronicle": [{"time_ms": 0.3, "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b", "hop": 1}], "title": "Blank", "command": {"announce": {}}, "to_unit": "a789ada1-edb5-4cfe-b1f9-8584abbf8a2f", "from_unit": "3c82ef61-0875-41d3-99ba-101672d79d6b", "response": {}}
        #getURL = "http://127.0.0.1:8000/api/tasks/to_unit/"+ u + "/?board=Backlog"
        #print type(data)
        #data = json.dumps(data)
        
        print type(data)
        
        {"key": "value"}
        response = requests.post(url = request_url,
                         json = data)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()