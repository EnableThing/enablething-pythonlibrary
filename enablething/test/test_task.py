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
from .. import taskobj
from .. import taskboardobj

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

    

    def test_update_configuration(self):

        c = configmanage.ThingConfiguration()
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
        
        c = configmanage.ThingConfiguration()
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
    def test_add(self):
        # Taskboard - Add and remove a task 
        id = uuid.uuid4().hex
        taskboard = taskboardobj.Taskboard(id)
        task = taskobj.Task(unit_id = id, from_unit = uuid.uuid4().hex, to_unit = uuid.uuid4().hex)
        task_id = task.task_id
        taskboard.add(task)
        search_task = taskboard.find_task(task.task_id)
        # Expect to find the task we have just added
        self.assertEquals(task_id, search_task.task_id)
        
        taskboard.remove(task) 
        self.assertRaises(LookupError, lambda: taskboard.find_task(task_id))

          

    
    #unittest.skip("Skip clock")
    def test_taskboard(self):
        # Taskboard - Add and remove a task 
        from_id = uuid.uuid4().hex
        to_id = uuid.uuid4().hex
        taskboard = taskboardobj.Taskboard(from_id)
        task = taskobj.Task(unit_id = from_id, from_unit = from_id, to_unit = to_id)
        expected_task_id = task.task_id
        taskboard.add(task)
        task = taskboard.find_task(task.task_id)
        # Expect to find the task we have just added
        self.assertEquals(expected_task_id, task.task_id)
        
        taskboard.remove(task)
        self.assertRaises(LookupError, taskboard.find_task, expected_task_id)

    #unittest.skip("Skip clock")
    def test_request(self):
        from_unit = uuid.uuid4().hex
        taskboard = taskboardobj.Taskboard(uuid.uuid4().hex)

        command = {"test":"test"}
        to = uuid.uuid4().hex

        task = taskobj.Task(unit_id = from_unit, command = command, to_unit = to, from_unit = from_unit)
        
        # Pass a dict object to to taskboard.request
        taskboard.request(to, command)
        
        print "task_id", taskboard.tasks[0].task_id
        
        
        r= taskboard_interface.get_task(taskboard.tasks[0].task_id)
        print r
        t = r['task_id']
        print t
        self.assertEquals(t,taskboard.tasks[0].task_id)
    
    #unittest.skip("Skip clock")
    def test_listen_for_response(self):
        taskboard = taskboardobj.Taskboard(uuid.uuid4().hex)
        
        command = {"test":"test_listen_for_response"}
        to = uuid.uuid4().hex
        
        # Create a task
        task = taskboard.request(to, command)
        print "posted task", task.json()
        

        # Should be no response.
        self.assertFalse(task.isResponse())
        
               
        response = {"test":"test"}
        taskboard.respond(task.task_id, response)
        
        self.assertTrue(task.isResponse())
            
    
    #unittest.skip("Skip clock")
    def test_newunitaanounce(self):
        
                         
        # Instantiate new_unit depending on unit_class
         
        testunit = configure_unit(unit_setup = unit.GenericUnit)
        # Run unit ... which should generate an "announce"
        
        testunit.get_task()
        
        print testunit.taskboard.last_removed_task_id()
        
        task = taskboard_interface.get_task(testunit.taskboard.last_removed_task_id())
        

        print task['command'], "announce" in task['command']
        self.assertTrue("announce" in task['command'])
        
       


    #unittest.skip("Skip clock")
    def test_create(self):
        # Create a random task and return JSON string
        
        random_task = taskboard_interface.create_random_task()
        
        
        to_unit = random_task['to_unit']
               
        # Take a JSON string task and post it to the task board
        # Return a requests object with .content as JSON string

        uploaded_task = taskboard_interface.post_task(random_task)

        to_unit_uploaded = uploaded_task['to_unit']
        task_id_uploaded = uploaded_task['task_id']
        
        self.assertEqual(to_unit,to_unit_uploaded)
        
        
        # Post a string containing task_id
        # Return a .content as JSON string
        downloaded_task = taskboard_interface.get_task(task_id_uploaded) 
        #taskboard_interface.get_task("08f0d24e22ff4cc9a7d1d686eac13ae2").content    
        task_id_downloaded = downloaded_task['task_id']
        self.assertEqual(task_id_downloaded, task_id_uploaded)
        print "to_unit",to_unit
        # Get tasks from the same unit    
        all_tasks_to_same_unit = taskboard_interface.get_new_tasks(to_unit)
        print "---",all_tasks_to_same_unit
        
        tasks = []
        for t in all_tasks_to_same_unit:
            tasks.append(t['task_id'])
    
        if task_id_uploaded in tasks:
            isUploaded = True
        else:
            isUploaded = False
        
        self.assertTrue(isUploaded)
    
        # Pick the first task as there should alway be one,
        # the one we just created.
        task_id = tasks[0]
    
        patch_data = {"response": {"blank":"123457"}}
        patched_task = taskboard_interface.patch_task(task_id,patch_data)
    
        # Check the task just patched by a GET request
        downloaded_patched_task = taskboard_interface.get_task(task_id)    
        downloaded_response = downloaded_patched_task['response']
        
        expected_response = patch_data['response']
        self.assertEqual(downloaded_response, expected_response) 

    #unittest.skip("Skip clock")
    def test_create_random_task(self):
        random_task = taskboard_interface.create_random_task()
        # Check this returns a dictionary object with       
        self.assertTrue(type(random_task) == dict)
        
        
    #unittest.skip("Skip clock")
    def test_taskboard_nocomplete(self):
        # Test tp make sure the get_new_tasks does not contain 
        # complete items.
        
        random_task = taskboard_interface.create_random_task()
        
        # Convert this task to a dictionary
        random_task_dict = random_task
        to_unit = random_task_dict['to_unit']

        random_task_dict['board'] = 'Complete'
        
        random_task = random_task_dict
                       
        # Take a JSON string task and post it to the task board
        # Return a requests object with .content as JSON string

        uploaded_task = taskboard_interface.post_task(random_task)

        task_id_uploaded = uploaded_task['task_id']
        
        # Get tasks from the same unit    
        all_tasks_to_same_unit = taskboard_interface.get_new_tasks(to_unit)
                
        
        test_outcome = True
        
        for t in all_tasks_to_same_unit:
            print t['board']
            if t['board']=='Complete':
                test_outcome = False
                
            
                
        self.assertTrue(test_outcome) 


        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()