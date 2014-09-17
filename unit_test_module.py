'''
Created on Aug 24, 2014

@author: nick
'''

import unit
import json, time, uuid
import taskboard_interface
import unittest


def configure_unit(id = uuid.uuid4().hex, input_ids = [], update_cycle = 1):
    # Load GUID list from configuration in GUID list
    unit_config = {
                        "common": {
                            "configurable": {
                                "fallback_UUIDs": ["a"],
                                "input_UUIDs": input_ids,
                                "memory_UUID": "g",
                                "taskboard_id": "t",
                                "forecaster_id": "h",
                                "fail_to": "6",
                                "update_cycle": 60,
                                "location": "i",
                                "security": "off",
                                "communication": {
                                    "type": "REST",
                                    "address": ["j","k"]
                                    }
                                },                      
                            "non-configurable": {
                                "unit_id": id,
                                "description": "Description of device",
                                "function": "thermometer",
                                "status": "ready",
                                "last_error": "OK"
                                }
                            },
                         "unit_specific": {
                                "configurable": {},
                                "non-configurable": {}
                            
                        }
                    }
    
    return unit.GenericUnit(unit_config)

def configure_clockunit(id = uuid.uuid4().hex, input_ids = [], update_cycle = 0):
    # Load GUID list from configuration in GUID list
    unit_config = {
                        "common": {
                            "configurable": {
                                "fallback_UUIDs": [],
                                "input_UUIDs": [],
                                "memory_UUID": "g",
                                "taskboard_id": "t",
                                "forecaster_id": "h",
                                "fail_to": "6",
                                "update_cycle": 60,
                                "location": "i",
                                "security": "off",
                                "communication": {
                                    "type": "REST",
                                    "address": ["j","k"]
                                    }
                                },                      
                            "non-configurable": {
                                "unit_id": id,
                                "description": "Test clock unit",
                                "function": "clock",
                                "status": "ready",
                                "last_error": "OK"
                                }
                            },
                         "unit_specific": {
                                "configurable": {},
                                "non-configurable": {}
                            
                        }
                    }
    return unit.ClockUnit(unit_config)


class Test_Taskboard(unittest.TestCase):
    
            
# Open JSON configuration file
# Check JSON configuration file complies with expected format
# Change a setting in JSON configuration file
# 
# Instatiate MemoryUnit and write memory
# Read memory from MemoryUnit
#  
# Check for a new task sent to a specific unit (Listen for unit_id)
# Check fail conditions - task board for a response to a specific task (Listen for task_id)

# Check success condition - task board for a response to a specific task (Listen for task_id)
# 
# SimpleForecastUnit - Check a forecast is provided for the next hour that matches the last reading.
# 
# Weather unit - Get current web temperature for current location 
# 
# AND unit- Instantiate and perform AND function with 2 inputs and 5 inputs
# OR unit- Instantiate and perform AND function with 2 inputs and 5 inputs
# NOT unit- Instantiate and perform AND function with 1 input
# XOR unit- Instantiate and perform AND function with 2 inputs and 5 inputs
  
    
    #unittest.skip("Skip clock")   
    def test_inputs(self):
        from_unit = uuid.uuid4().hex
        
        task1 = unit.Task(from_unit = from_unit, to_unit = uuid.uuid4().hex)
        task2 = unit.Task(from_unit = from_unit, to_unit = uuid.uuid4().hex)
        
        #input1 = unit.Input_Request(task1)
        #input2 = unit.Input_Request(task2)
        input_set = unit.Input_Set([task1, task2])
        
        input1 = input_set.requests[0]
        input2 = input_set.requests[1]
        
        print input_set.debug()
        self.assertFalse(input1.isResponse())
        self.assertFalse(input2.isResponse())
        
        self.assertFalse(input_set.isResponse())
        
        input1.input_received(task1)
        
        print input_set.debug()
        self.assertTrue(input1.isResponse())
        self.assertFalse(input2.isResponse())
        
        self.assertFalse(input_set.isResponse())
        
        input2.input_received(task2)
        
        print input_set.debug()
        self.assertTrue(input1.isResponse())
        self.assertTrue(input2.isResponse())
        
        self.assertTrue(input_set.isResponse())

    #unittest.skip("Skip clock")        
    def test_process(self):
        unit = configure_unit(id = uuid.uuid4().hex)
        unit.get_task()
        unit.get_task()
        unit.get_task()
        print unit.memory.json()
        self.assertTrue('forecast' in unit.memory.json())
        self.assertTrue('history' in unit.memory.json())
    
   
    def test_clock(self):
        # Setup a clock unit and request the time       
        clock_unit = configure_clockunit(update_cycle = 0)
        # Process announce
        clock_unit.get_task()
                
        masterunit_id = uuid.uuid4().hex
        masterunit = configure_unit(id = masterunit_id, input_ids = [clock_unit.id], update_cycle = 0)
        
        # Process announce
        masterunit.get_task()
       
        # Create a reading 
        clock_unit.get_task()
        print clock_unit.taskboard.debug()
        
        # Trigger a request_inputs 
        # Normally this would be at the poll interval

        set_id = masterunit.request_inputs()
               
        clock_unit.get_task()
            
        self.assertFalse(masterunit.inputboard.isResponse(set_id))
        
        masterunit.get_task()
        
        task_id = masterunit.taskboard.last_removed_task_id()
        
        masterunit.get_task()
              
        task = taskboard_interface.get_task(masterunit.taskboard.last_removed_task_id())
        
        #print task['command'], "output" in task['command']
        #print task['response'], "dummy reading" in task['response']
        self.assertTrue("output" in task['command'])
        self.assertTrue("history" in task['response'])
        self.assertTrue("forecast" in task['response'])
        
        self.assertTrue(masterunit.inputboard.isResponse(set_id))
        
    #unittest.skip("Skip clock")        
    def test_taskboard_addtask(self):
        # Taskboard - Add and remove a task 
        id = uuid.uuid4().hex
        taskboard = unit.Taskboard(id)
        task = unit.Task(from_unit = uuid.uuid4().hex, to_unit = uuid.uuid4().hex)
        
        task_id = task.task_id
        
        taskboard.add(task)
        
        search_task = taskboard.find_task(task.task_id)
        # Expect to find the task we have just added

        self.assertEquals(task_id, search_task.task_id)
        print "---", task_id,task.task_id
        print taskboard.debug()
        taskboard.remove(task)
        print taskboard.debug()
        
        self.assertRaises(LookupError, lambda: taskboard.find_task(task_id))

    #unittest.skip("Skip clock")
    def test_request_multiple_inputs(self):
        # Create two units
        testunit1_id = uuid.uuid4().hex
        #testunit1 = configure_unit(id = testunit1_id)

        testunit2_id = uuid.uuid4().hex
        #testunit2 = configure_unit(id = testunit2_id)
        
        masterunit_id = uuid.uuid4().hex
        
        testunit1 = configure_unit(id = testunit1_id)
        testunit2 = configure_unit(id = testunit2_id)
        
        masterunit = configure_unit(id = masterunit_id, input_ids = [testunit1.id,testunit2.id])
          
              
        self.assertTrue(masterunit.status == "new")

        # Instantiate new_unit depending on unit_class
        masterunit.get_task()
                
        # This should trigger an "announce" and change status to "ready"
        # Tested under another test case
        print masterunit.taskboard.debug()
        print testunit1.taskboard.debug()
        print testunit2.taskboard.debug()
        
        self.assertTrue(masterunit.status == "ready")
        
        # This should trigger two requests for input, one to each input unit                              
        masterunit.request_inputs()
        
        tasks = []
        for task in masterunit.taskboard.tasks:
            tasks.append(task)
            
        testunit1.get_task()
        testunit1.get_task()
        
        testunit2.get_task()
        testunit2.get_task()

        masterunit.get_task()
         
        self.assertTrue(len(tasks)==2)
        for task in tasks:
            response = taskboard_interface.get_task(task.task_id)
            self.assertNotEqual(response["response"], "{}")
        
                
            

    
    #unittest.skip("Skip clock")
    def test_taskboard(self):
        # Taskboard - Add and remove a task 
        from_id = uuid.uuid4().hex
        to_id = uuid.uuid4().hex
        taskboard = unit.Taskboard(from_id)
        task = unit.Task(from_unit = from_id, to_unit = to_id)
        expected_task_id = task.task_id
        taskboard.add(task)
        task = taskboard.find_task(task.task_id)
        # Expect to find the task we have just added
        self.assertEquals(expected_task_id, task.task_id)
        
        taskboard.remove(task)
        self.assertRaises(LookupError, taskboard.find_task, expected_task_id)

    #unittest.skip("Skip clock")
    def test_task_request(self):
        from_unit = uuid.uuid4().hex
        taskboard = unit.Taskboard(uuid.uuid4().hex)

        command = {"test":"test"}
        to = uuid.uuid4().hex

        task = unit.Task(command = command, to_unit = to, from_unit = from_unit)
        
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
        taskboard = unit.Taskboard(uuid.uuid4().hex)
        
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
    def test_command_request(self):
        
        #askboard = unit.Taskboard(uuid.uuid4().hex)
        command = {"announce":""}
        task = unit.Task(command = command,to_unit = uuid.uuid4().hex, from_unit=uuid.uuid4().hex)
        
        x = task.get()
        print "...",x
        #new_unit = unit.Command()
        
        # = taskboard.request(command )
        #rint x
    
    #unittest.skip("Skip clock")
    def test_newunitaanounce(self):
        
                         
        # Instantiate new_unit depending on unit_class
         
        testunit = configure_unit()
        # Run unit ... which should generate an "announce"
        
        testunit.get_task()
        
        print testunit.taskboard.last_removed_task_id()
        
        task = taskboard_interface.get_task(testunit.taskboard.last_removed_task_id())
        

        print task['command'], "announce" in task['command']
        self.assertTrue("announce" in task['command'])
        
       

    @unittest.skip("Skip polling test")    
    def test_poll_start(self):
        poll = unit.Poll(5)

        # Should be false when started.
        self.assertFalse(poll.isTrigger())
    @unittest.skip("Skip poll trigger test")     
    def test_poll_trigger(self):
        poll = unit.Poll(5)
        # Should be false when started.       
        time.sleep(7)
        self.assertTrue(poll.isTrigger())

    @unittest.skip("Skip poll not triggered test")
    def test_poll_nottrigger(self):
        poll = unit.Poll(5)
        # Should be false when started.       
        time.sleep(2)
        self.assertFalse(poll.isTrigger())

    #unittest.skip("Skip clock")
    def test_taskboard_createtask(self):
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