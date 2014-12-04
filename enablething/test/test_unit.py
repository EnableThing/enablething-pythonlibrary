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
from unit import Unit, TaskSet, TaskSetHandler

import logging

from wsgiref.simple_server import make_server
import threading

from restlite import restlite
from enablething.thing import RestHandler

def setup_server(units):
    rest_handler = RestHandler()    
    rest_handler.configure(units)
    print "routes",rest_handler.routes
    httpd = make_server('', 8080, restlite.router(rest_handler.routes))

    httpserver = threading.Thread(target=httpd.serve_forever)
    httpserver.setDaemon(True)
    httpserver.start()  

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
    valid_command = Task(unit_id, **valid_json_dict)
    valid_response = Task(unit_id, **valid_json_dict)
    valid_response.add_response(response = {"response":"yes"})
    
    return valid_command, valid_response   

class Test_Rest(unittest.TestCase):
    def setUp(self):
        # Test cases for valid command and valid response   
        self.command, self.response = create_valid_task()                     
                                         
    def test_init(self):
        ip = "127.0.0.1"
        port = 8080
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        testunit = Unit(ip, unit_id, fallback_units = [uuid.uuid4().hex, uuid.uuid4().hex])
        
        setup_server([testunit])
        
        self.assertTrue(testunit.rest.url == "http://127.0.0.1:8080")
        self.assertTrue(testunit.unit_id == unit_id)
    
    def test_post_task(self):
        ip = "127.0.0.1"
        port = 8080
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        testunit = Unit(ip, unit_id, fallback_units = [uuid.uuid4().hex, uuid.uuid4().hex])
        setup_server([testunit])
        
        command, response = create_valid_task()
        # Posting a task should result in no error
        testunit.post_task(command)
        
        # Posting test again should raise an error
        try:
            testunit.post_task(command)
        except HTTPError as e:
            status_code = e.response.status_code
            
        self.assertTrue(status_code == 500)
        
        # Posting a response to the task should not result in an error
        testunit.post_task(response)
        
    def get_new_responses(self):
        self.assertTrue(False)

    def test_get_response(self):
        ip = "127.0.0.1"
        port = 8080
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        testunit = Unit(ip, unit_id, fallback_units = [])
        setup_server([testunit])
        
        # Create a valid command and response to use in this test
        command, response = create_valid_task()
        
        # Post a command, no exception
        testunit.post_task(command)
        
        # Post a response, no exception
        testunit.post_task(response)
        
        testunit_response = testunit.get_response(command)
        self.assertTrue(isinstance(testunit_response, Task))
        self.assertTrue(testunit_response.task_id == response.task_id )
        print response
        
    def test_get_new_commands(self):
        ip = "127.0.0.1"
        port = 8080
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        testunit = Unit(ip, unit_id, fallback_units = [])
        setup_server([testunit])
        # Post five tasks to taskboard
        
        for _ in xrange(5):
            command, response = create_valid_task()
            # Posting a task should result in no error
            testunit.post_task(command)
        for _ in xrange(5):
            command, response = create_valid_task()
            # Posting a task should result in no error
            testunit.post_task(response)
        
        tasks = testunit.get_new_commands()
        for task in tasks:
            self.assertTrue(task.response == {})
            
    def test_get_new_responses(self):
        ip = "127.0.0.1"
        port = 8080
        unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        testunit = Unit(ip, unit_id, fallback_units = [])
        setup_server([testunit])
        # Post five tasks to taskboard
        
        for _ in xrange(5):
            command, response = create_valid_task()
            # Posting a task should result in no error
            testunit.post_task(command)
        
        for _ in xrange(5):
            command, response = create_valid_task()
            # Posting a task should result in no error
            testunit.post_task(response)
        
        tasks = testunit.get_new_responses()
        for task in tasks:
            self.assertTrue(task.response <> {})
    
    def test_taskset_isresponse(self):
        
        command1, response1 = create_valid_task()
        command2, response2 = create_valid_task()
        
        taskset = TaskSet([command1])
        self.assertTrue(taskset.isResponse() == False)
        
        taskset = TaskSet([response1])
        self.assertTrue(taskset.isResponse() == True)
        
        taskset = TaskSet([command1, response2])
        self.assertTrue(taskset.isResponse() == False)
        
        taskset = TaskSet([response1, response2])
        self.assertTrue(taskset.isResponse() == True)

    def test_taskhandler_next(self):
        
        command1, response1 = create_valid_task()
        command2, response2 = create_valid_task()
        
        
        tasksethandler = TaskSetHandler()
        tasksethandler.add_taskset([command1, command2])
        
        self.assertTrue(tasksethandler.tasksets[0].tasks[0].task_id == command1.task_id)
        self.assertTrue(tasksethandler.tasksets[0].tasks[1].task_id == command2.task_id)
        
        tasksethandler.add_taskset([command1, response2])
        #tasksethandler.add_taskset(taskset3)
        
        # Should fail
        self.assertRaises(LookupError, lambda: tasksethandler.next())
        
        tasks = [response1, response2]
        tasksethandler.add_taskset(tasks)
        self.assertTrue(tasksethandler.tasksets[2].tasks[0].task_id == response1.task_id)
        self.assertTrue(tasksethandler.tasksets[2].tasks[1].task_id == response2.task_id)
        
        # Should return taskset3
        taskset = tasksethandler.next()
        self.assertRaises(IndexError, lambda: tasksethandler.tasksets[2].tasks[0].task_id)
        self.assertTrue(taskset.tasks[0].task_id == response1.task_id)
        self.assertTrue(taskset.tasks[1].task_id == response2.task_id)
        
        tasksethandler.add_taskset([command1, command2])
        
        for taskset in tasksethandler.tasksets:
            self.assertFalse(taskset.isResponse())
        
        command1.response = {"yes":"yes"}
        command2.response = {"yes":"yes"}
                             
        for taskset in tasksethandler.tasksets:
            self.assertTrue(taskset.isResponse())
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()