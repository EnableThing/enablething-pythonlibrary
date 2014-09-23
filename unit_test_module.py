'''
Created on Aug 24, 2014

@author: nick
'''

import unit
import unit_custom
import json, time, uuid
import taskboard_interface
import unittest



import logging

# create logger
logging.basicConfig(filename='log.log',level=logging.DEBUG)
       

def configure_unit(unit_setup = unit.GenericUnit, id = None, input_ids = [], update_cycle = 5, description = "Generic unit"):
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
                            "non-configurable": {
                                "unit_id": id,
                                "description": description,
                                "function": "display",
                                "status": "ready",
                                "last_error": "OK"
                                }
                            },
                         "unit_specific": {
                                "configurable": {},
                                "non-configurable": {}
                            
                        }
                    }
  
    return unit_setup(unit_config)



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


    def test_PassThruUnit(self):
        inputunit = configure_unit(unit_setup = unit.GenericUnit, input_ids = [], update_cycle = 0, description = "Input unit - clock")
        print "INPUTUNIT.ID", inputunit.id
        processunit = configure_unit(unit_setup = unit.PassThruUnit, input_ids = [inputunit.id], update_cycle = 0, description = "PassThruUnit unit")
        print "PROCESSUNIT.ID", processunit.id
        # Process announces
        start_time = time.time()
        while time.time() - start_time < 2:
            inputunit.get_task()
            processunit.get_task()
            
        # Should be no memory initially on inputunit       
        self.assertTrue('dummy_reading' in inputunit.memory.history[0].data)
        
        print "test inputunit.memory.history"

        for i in inputunit.memory.history:
            print "inputunit.memory", i.time_stamp, i.data
        
        print "test processunit.memory"

        for i in processunit.memory.history:
            print "processunit.memory", i.time_stamp, i.data
        
        print "test processunit.inputboard.input_container"
        
        for input_container in processunit.inputboard.input_container:
            for i in input_container.history:
                print "i", i
                print "processunit.inputboard.input_container.history", i.time_stamp, i.data

        self.assertTrue('dummy_reading' in processunit.memory.history[0].data)
        self.assertTrue('dummy_reading' in processunit.inputboard.input_container[0].history[0].data)
 
 

    #unittest.skip("Skip")
    def test_response_chain(self):
        inputunit = configure_unit(unit_setup = unit.ClockUnit, input_ids = [], update_cycle = 0, description = "Clock unit")
        processunit = configure_unit(unit_setup = unit.PassThruUnit, input_ids = [inputunit.id], update_cycle = 0, description = "Pass-through unit")
        outputunit = configure_unit(unit_setup = unit_custom.charOutputUnit, input_ids = [processunit.id], update_cycle = 0, description = "Output unit")

        start_time = time.time()
        while time.time() - start_time < 2:
            inputunit.get_task()
            processunit.get_task()
            outputunit.get_task()
            
        for i in inputunit.memory.history:
            print "input.memory", i.time_stamp, i.data
            
        for i in processunit.memory.history:
            print "processunit.memory", i.time_stamp, i.data
            
        for i in outputunit.memory.history:
            print "outputunit.memory", i.time_stamp, i.data

        for input_container in processunit.inputboard.input_container:
            for i in input_container.history:
                print "i", i
                print "processunit.inputboard.input_container.history", i.time_stamp, i.data        
        
        for input_container in outputunit.inputboard.input_container:
            for i in input_container.history:
                print "i", i
                print "outputunit.inputboard.input_container.history", i.time_stamp, i.data
                   
        self.assertTrue('time' in outputunit.memory.history[0].data)
        
    #unittest.skip("Skip")        
    def test_display(self):
        # Setup a clock unit and request the time
        display_unit = configure_unit(unit_setup = unit_custom.charOutputUnit)   
        
        # Process announce
        rtn = display_unit.display_interface("ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOP")
                  
        self.assertEqual(rtn, "ABCDEFGHIJKLMNOP/nQRSTUVWXYZABCDEF")   
        
    #unittest.skip("Skip clock")        
    def test_process(self):
        test_unit = configure_unit(unit_setup = unit.GenericUnit, id = uuid.uuid4().hex, update_cycle = 0)
        
        start_time = time.time()
        while time.time() - start_time < 1:
            test_unit.get_task()
        
        print test_unit.memory.json()
        self.assertTrue('forecast' in test_unit.memory.json())
        self.assertTrue('history' in test_unit.memory.json())
    
    #unittest.skip("Skip")
    def test_clock(self):
        # Setup a clock unit and request the time       
        clock_unit = configure_unit(unit_setup = unit.ClockUnit, description = "Clock unit", update_cycle = 0)
        # Process announce
        clock_unit.get_task()
                
        masterunit_id = uuid.uuid4().hex
        masterunit = configure_unit(unit_setup = unit.GenericUnit, id = masterunit_id, input_ids = [clock_unit.id], description = "Master unit", update_cycle = 60)
        
        start_time = time.time()
        while time.time() - start_time < 1:
            # Process announce
            masterunit.get_task()
            # Create a reading 
            clock_unit.get_task()
        
        self.assertTrue('time' in clock_unit.memory.history[0].data)
  
        
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
        
        testunit1 = configure_unit(unit_setup = unit.GenericUnit, id = testunit1_id)
        testunit2 = configure_unit(unit_setup = unit.GenericUnit, id = testunit2_id)
        
        masterunit = configure_unit(unit_setup = unit.GenericUnit, id = masterunit_id, input_ids = [testunit1.id,testunit2.id])
          
              
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
         
        testunit = configure_unit(unit_setup = unit.GenericUnit)
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