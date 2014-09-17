#unit.py
#Unit library


import uuid
import time
import taskboard_interface
from datetime import datetime
import json

class Poll(object):
    def __init__(self, poll_interval):
        self.start_time = time.time()        
        self.poll_interval = poll_interval
        


    def restart(self):
        self.start_time = time.time()


    def isTrigger(self):
        # Return True if triggered

        if time.time() > self.start_time + self.poll_interval:
            isTrigger = True
            self.restart()
        else:
            isTrigger = False

        return isTrigger




class DataPoint(object):
    def __init__(self, time_stamp, data):
        self.timestamp = time_stamp
        self.data = data


class Memory(object):
    def __init__(self):
        self.time_range = {        
"past":-10000,
"future":10000
}
        self.history = []
        self.forecast = []


    def add(self, datapoint):
        self.history.insert(0, datapoint)


    def remove(self, datapoint):
        self.history.remove(datapoint)


    def replace_history(self, new_history):
        # new_history is a json string {"point 1":{"time_stamp":time,
        #   "datapoint":data},"point 2":{...}}
                for point in new_history:
                        self.add(point)
        
#    def update_history(self, new_history):
    # TBD


    def update_forecast(self):
        # Make a call to the forecast unit using self.history
        # TBD
        pass


    def trim(self, low, high):
        # Provide data set from low to high only
        raise Exception
        memory = []
        return memory
    
    def current_value(self):
        return self.history.pop()
    
    def json(self):
        # Create a dictionary
        json_dict = {
                "history":self.history,
                "forecast":self.forecast
                }
        return json_dict
    
class Task(object):
    def __init__(self, **kwargs):

        options = {
            'task_id' : "",
            'board' : 'Backlog',
            'command' : {},
            'response' : {},
            }

        options.update(kwargs)
        

        
        #for key, value in kwargs.iteritems():
        for key, value in options.iteritems():

            setattr(self,key, value)     
        
        print self.command
        
        if self.command == "{}":
            raise Exception("Cannot create a new task with a blank command")
        #if self.task_id <> "":
        #    print "Created a new id"
        #    raise Exception("Attempting to send an id to task create")
        
        t = self.json()
        print "self.task_id", self.task_id
        if self.task_id == "":
            # We are creating a task that does not
            # already exists on the master board, so
            # post it and get task_id number.
            r = taskboard_interface.post_task(t)
            self.task_id = r['task_id']
        
        self.json()
        
    def command_instruction(self):

        j = self.command
        
#
        
        key = []
        value = []
        for k, v in j.iteritems() :
            key.append(k)
            value.append(v)
        if len(key) <> 1:
            raise LookupError("Too many commands in command")
        
        return key.pop(), value.pop()
        
    def get(self):
        taskboard_interface.get_task(self.task_id)
        task = taskboard_interface.get_task(self.task_id)

        return task
                           
    def update(self, **kwargs):
      
        # kwargs is a dictionary
        # this will require some form of validation to ensure only valid keys are created.  TBD.

        json_dict = {}
        for key, value in kwargs.iteritems():
            print "key",key,"value", value
            json_dict[key] = value
            setattr(self,key, value)
        
        self.json()

        taskboard_interface.patch_task(self.task_id,json_dict)

    def progress(self):
        self.update(board = 'In progress')
        #taskboard_interface.patch_task(task.task_id,{"board":task.board})
        #     self.update(task) 
        
        
#     def request(self):
#         #self.command = {"command":command,"information":information}
# #        try:
#         
#         t = self.json()
# 
#         r = taskboard_interface.post_task(t)
#         
#         self.task_id = r['task_id']
#         self.json()
#         
#         return self.task_id

        
    def respond(self, response):
        self.update(response = response, board = 'Complete')
        
        #r = taskboard_interface.patch_task(self.task_id, {"response":self.response})


                   
        # If there is no exception then have successfully posted the response
        #self.is_response = True

    def listen_for_response (self):

        #Check the message board for a command sent to task_id
        # It will be a task that is Complete

        #task_list = taskboard_interface.get_new_tasks(self.task_id)
        task = taskboard_interface.get_task(self.task_id)
        if task['response'] <> {}:
            task.update(response = task['response'])
        
    
    def isResponse(self):
        self.listen_for_response()
        if self.response == {}:
            return False
        else:
            return True
            



    def print_console(self):
        #print "Task console print not yet implemented"
        
        print self.json()
        
    def json(self):
        # dumps ... dict to string
        # loads ... string to dict
        # Return a dict
        task_dict = {
                        "task_id" : self.task_id,
                        "title": "Blank",
                        "board": self.board, 
                        "from_unit": self.from_unit , 
                        "to_unit": self.to_unit , 
                        "command": self.command,
                        "response": self.response
                        }

        
        return task_dict
    def debug_task(self):
        print "task id: ",self.task_id
        print "board:   ", self.board
        print "to:      ", self.to_unit
        print "from:    ", self.from_unit
        print "command: ", self.command
        print "response:", self.response
        print


class Taskboard(object):
    # Implement an internal task board for managing tasks, adding, removing, 
    # and requesting new tasks from primary task board.

    def __init__(self,unit_id):
        self.tasks = []  
        self.from_unit = unit_id
        self.last_removed = None
    
    def last_removed_task_id(self):
        return self.last_removed
    
    def find_task(self,task_id):
        # Returns LookupError if no tasks found.
        # Returns task object if task found.
        task = [x for x in self.tasks if x.task_id == task_id]
        for t in task:
            print "task",t.json()
        if len(task) > 1:
            raise LookupError("Task lookup returned more than one task")
        if len(task) < 1:
            raise LookupError("Task lookup returned no tasks")
        
        
        #print "find_task -",task[0],"-"
        
        return task[0]
    
    def isEmpty(self):
        return self.tasks == []


    def add(self, task):
        self.tasks.insert(0, task)

    def update(self, task_id):
        task = self.find_task(task_id)
        task.update()
        
#       task_id = task.task_id
#         self.debug_tasks()
#         print "debug: task_id", task_id
#         task_to_remove = self.find_task(task_id)
#         
#         self.remove(task_to_remove)
#         self.add(task)
#        task

    def first(self):
        return self.tasks[0]
    
    def remove(self, task):
        print "Removing", task.task_id
        self.last_removed = task.task_id
        self.tasks.remove(task)


    def size(self):
        return len(self.tasks)
    
    def print_console(self):
        print "Active tasks"
        for q in self.tasks:
                q.print_console()

    def request (self, to_id, command):
        # Takes a dict command and creates a new task.
        # Generate a new task with a new UUID for the task
        task = Task(command = command, from_unit = self.from_unit, to_unit = to_id)
        #task.create(command = command, from_unit = self.from_unit, to_unit = to_id)
        

        #task.request()


        # Add task_uuid to array live_tasks.
        self.add(task)
        self.status = "waiting"

        return task

    def respond (self, task_id, response):

        task = self.find_task(task_id)
        # Check this
        # http://stackoverflow.com/questions/10858575/find-object-by-its-member-inside-a-list-in-python 
        task.update(response = response, board='Complete')
        #task.respond(response)

        # Remove this task from the task board

        self.status = "ready"


    #def listen_for_unitID (self, unit_id):
    def get_new_tasks(self, unit_id):
        new_tasks = []
        #Check the message board for a new command sent to UUID
        returned_tasks = taskboard_interface.get_new_tasks(unit_id)
        
        for returned_task in returned_tasks:
            task_id = returned_task['task_id']

            if returned_task['board'] == 'Backlog':
                try:
                    task = self.taskboard.find_task(task_id)
                    # Task exists already, don't take any action because it is still on the Backlog
                except:
                    # Task does not exist
                    task = Task(**returned_task)
                    task.update(board = 'In progress')
                    if len(task.command)>1:
                        raise Exception, "Too many keys in command"                    
                    new_tasks.append(task_id)
                
        return new_tasks
    

                

    def listen_for_response (self, task_id):

        return self.find_task(task_id).listen_for_response()
    
    
        
    def isResponse (self, task_id):

        
        return self.find_task(task_id).isResponse()

    def debug(self):
        print "Debug: taskboard", self.from_unit
        if len(self.tasks) ==0:
            print "<No tasks on task board>"
        else:
            for t in self.tasks:
                t.debug_task()
            



class Input_Request(object):
    def __init__(self, task):
        self.task = task
        self.input_id = task.to_unit
        #self.id = task.task_id
        self.request_time = time.time
        self.response_state = False

    #def response_status(self,state):
    #    self.isResponse = state
    def input_received(self,task):
        self.task = task
        self.response_state = True
        self.response_time = time.time

    def isResponse(self):
        return self.response_state
        

class Input_Set(object):
    def __init__(self, task_set):
        
        # Create a unique identifier for this input set
        self.id = uuid.uuid4().hex
        self.reset()
        
        #for inpt in input_ids:
        for task in task_set:
            self.add(task)
        
        # Fall back units if this input becomes unavailable
        #self.fallback_ids = fallback_ids
        #self.requests = []

        self.memory = Memory()
        
    def reset(self):
        self.requests = []

    def add(self, task):
        self.requests.insert(0, Input_Request(task))

    def remove(self, task):
        self.requests.remove(Input_Request(task))

    def isResponse(self):
        # Check all the input requests in the same set request
        for inpt in self.requests:
            if (inpt.isResponse() == False):
                # At least one response is False
                return False

        return True

    def process_input_set(self, memory):
        self.memory.replace_history(memory)
        # Need to add functionality to also replace forecast
        self.isResponse = True
        self.response_time = time.time
        
    def inputs_received(self, task):
        for inpt in self.requests:
            if inpt.id == task.id:
                inpt.task = task
                inpt.input_received()
                return
        raise LookupError("Task not found in input set")

    def debug(self):
        print "Debug: input_set"
        print "isResponse()",self.isResponse()
        for inpt in self.requests:
            print inpt.input_id, inpt.isResponse()

class Inputs(object):
    def __init__(self, input_ids, fallback_ids):
        # Keep track of the task_id that made this request.
        # Fixed object to point to "upstream" inputs to this unit.
  
        self.input_ids = input_ids
        self.fallback_ids = fallback_ids

        self.input_sets = []
        
#        self.add(input_ids, [])
    def find_set(self, set_id):
        for instance in self.input_sets:
            if set_id == instance.id:
                return instance
        raise LookupError("Set not found %s", set_id)
   
    def input_received(self,task):
        for instance in self.input_sets:
            for inpt in instance.requests:
                if inpt.task.task_id == task.task_id:
                    inpt.input_received(task)
                    return
        raise LookupError("Task not found in inputs")
        
       
           
    def remove_all(self):
        self.input_sets = []

    def add(self,task_set):
        i = Input_Set(task_set)
        self.input_sets.insert(0, i)

        return i
        
        

    def remove(self, inpt):

        raise NotImplemented
        self.input_sets.remove(Input_Set())

    def update_fallback(self, fallback_ids):
        raise NotImplemented
        #for instance in self.input_sets:
        #    if instance.id == input_id:
        #        instance.fallback_ids = fallback_ids
                 
    def isResponse(self, set_id):
        instance = self.find_set(set_id)
        return instance.isResponse()
    
    def debug(self):
        print "Debug output: inputboard"
        for instance in self.input_sets:
            print instance.isResponse()
            instance.debug()
            
            
class GenericUnit(object):
            
    def __init__(self,unit_config):

        
        # consider refactor for **kwargs
        configurable = unit_config["common"]["configurable"]
        non_configurable = unit_config["common"]["non-configurable"]
        self.json_config = unit_config

        # Apply configuration
        self.id = non_configurable["unit_id"]
        self.function = non_configurable["function"]
        self.description = non_configurable["description"]
        
        self.fallback_ids = configurable["fallback_UUIDs"]
        self.input_ids = configurable["input_UUIDs"]
        self.unit_type = "undefined"
        if self.input_ids == []:
            self.unit_type = "Input"
        self.memory_id = configurable["memory_UUID"]
        self.forecaster_id = configurable["forecaster_id"]
        self.fail_to = configurable["fail_to"]
        self.update_cycle = configurable["update_cycle"]

        # not implemented
        self.security = "off"
        self.communication = configurable["communication"]

        # Additional variables
        self.status = "new"
        
        self.taskboard = Taskboard(self.id)
        self.inputboard = Inputs(self.input_ids, self.fallback_ids)
        
        self.memory = Memory()
        self.input_poll = Poll(self.update_cycle)
        # "status": [New, Ready, Running, Waiting, Terminated],

        # Run start-up
        self.set_status("new")
        


    def unit_startup(self):
        # Unit start-up
        # Defined by inheriting class
        pass

    def request_inputs(self):
        print "request_inputs()", self.inputboard.input_ids
#         if self.inputboard.inputs <> []:
#              # Not all inputs were processed
#              # Need to figure out how to deal with this
 
        task_set=[] 
        for inpt in self.inputboard.input_ids:

            command = {"output":None}
            task = self.taskboard.request(inpt, command)
            task_set.append(task)
        
        s = self.inputboard.add(task_set)
        return s.id
    
            
        

    def update_memory(self,datapoint):
        # This is the function that updates the 
        # units internal memory


        #self.memory.replace_history(self.memory)
        #self.memory.update_forecast()
        self.memory.add(datapoint)



    def ondevice_display(self):
        # This will be custom for each unit and defined
        # by inheriting class.
        # For a typical python script, display to console.


        print "Status:",self.status


        print "Live Task IDs:"
        for t in self.tasks:
            t.print_console()


        # Display inputs


        # Display memory
    def set_status(self, state):
        valid_states = {'new', 'terminated', 'waiting', 'ready'}
        if 'new' not in valid_states:
            raise Exception
        self.status = state

    
    def new(self):
        # Common startup up procedure
        print ">>>>>>>>>>NEW"

        command = {"announce":{"fallback_ids":self.fallback_ids}}
        # Announce using own id for to_unit as this is not addressed to any specific unit
        self.taskboard.request(self.id, command)

        # Unit specific startup
        self.unit_startup()


        self.set_status("ready")


    def terminated(self):
        # Listen for a possible command to re-start the unit.
        task = self.listen_for_unitID(self.id)


        if task.command == "start":
            newtask = self.taskboard.request(self.id, task.command)
            #self.taskboard.add(newtask)

        self.set_status("ready")

    def waiting(self):
        # Device didn’t update last cycle, so unit
        # has been put into "Waiting" state
        # Address this error condition, which is
        # likely caused by waiting for input
        # Check whether all inputs were received.
        # Try again to contact offending inputs,
        # fallback to alternative inputs if not.
        # This is where fallback and resilience is encoded.
        # Use fail_to variable to decide how to respond.


        # For now though, 
        self.set_status("ready")


    
    def ready(self):

        # Check if any input sets have been received
        print "Checking input sets"
        for input_set in self.inputboard.input_sets:
            print "set_id",input_set.id
            print input_set.isResponse()
            
            
    
        if self.input_poll.isTrigger(): 
                # Request inputs at a specific interval
                self.request_inputs()
                self.set_status("ready")
                print "poll triggered"

        

# Check for the condition where the unit’s process
# hasn’t been able to run because not all 
# information received.


##If last run of units process > minimum_cycle_update,
##    self.status = "waiting"

        # Check for new tasks
        print "Debug reminder: make this at a poll interval rather than every loop"
        self.taskboard.get_new_tasks(self.id)

        # Get next message from message store for this unit’s GUID
        # Unit is ‘ready’ so it is ready to process a received command.
              
        if len(self.taskboard.tasks) > 0:

            command = None
            instruction = None
            # There are tasks waiting to be processed
            # Pop the earliest task and process it
            task = self.taskboard.first()
            print "json of task being processed", task.json()
                                 
            command = task.command.keys()[0]
            instruction = task.command.get(command)
                
            if command == "announce":
                print "Command received - announce"
                #State this devices GUID and fallback GUIDs
                task.respond({"fallback_ids":self.fallback_ids})
                #self.respond (task,)
#                     task.update(board = "Complete")
                self.taskboard.remove(task)
    
            if command == "start":
                print "Command received - start"
                # Start this device
                # No action, device is already running.
                task.respond({"status":self.set_status})
                self.taskboard.remove(task)
    
            if command == "terminate":
                print "Command received - terminate"
                # Organization chart process will handle
                # this, as will fall-back 
                # process in other units.
                self.set_status("terminated")
                task.respond({"status":self.set_status})
                self.taskboard.remove(task)
    
    
            if command ==  "clone":
                print "Command received - clone"
                # if possible, create a copy of this unit
                # with a new UUID
                # not possible for hardware units
                response = {"success":False,
                            "unit_id":None}
                task.respond(response)
                self.taskboard.remove(task)
                self.set_status("ready")
                
                #<< Unit specific code>>
                
    
            if command == "setting":
                print "Command received - setting"
                # Change configuration of this unit
                # Check received setting for validity
    
    
                # Update configuration in persistent
                # memory to received setting
    
    
                with open('config.json', 'w') as f:
                    json.dump(instruction, f)
                self.set_status("new")
                self.taskboard.remove(task)
    
            if command == "configuration":
                print "Command received - configuration"
                # Respond with this units configuration
 
                task.respond(task.response)
                task.remove()
                self.set_status("ready")
    
            if command == "output": 
                print "Command received - output"
                # respond with Memory ie (horizon) history and forecast
                # Provides Memory of output
                task.respond(self.memory.json())
                self.inputboard.input_received(task)
                self.taskboard.remove(task)               
                self.set_status("ready")
                
            if command == "memory":
                print "Command received - memory"
                print "memory" 
                # Overwrite units Memory ie (horizon) history and forecast
                # This is typically used to update memory variable so is common
                # to all devices.  If it is a memory unit the memory is updated, for
                # other units it resets the unit memory.
                self.update_memory(instruction)
                self.taskboard.remove(task)
            
        

        
#         # Check for responses to tasks issed by this unit
#         
#         for task in self.taskboard.tasks:
#             
#                
#             print "Processing task on taskboard", task.json()
#             #if task.from_unit == self.id and task.isResponse():
#             if True:
#                 
#                 command, instruction =  task.command_instruction()
#                 
#                 if command == "announce":
#                     print "Processing task - announce"
#                     # Response to an announce request
#                     # in format {"fallback_ids": ..}
#                     #Adjust GUID_fallback variables if needed
#                     # task.respond.keys
#                     if 'fallback_ids' in instruction:
#                         self.fallback_ids = instruction["fallback_ids"]
# 
#                     task.update(board = "Complete")
#                     self.inputboard.input_received(task)
#                     task.remove()
# 
#                 
#                 if command == "start":
#                     print "Processing task - start"
#                     # This is an acknowledgement -
#                     # check no error returned.
#                     task.remove()
#                     
# 
#                 if command == "terminate":
#                     print "Processing task - terminate"
#                     # remove this unit from organization
#                     # chart
#                     # this is an acknowledgement
#                     # - check no error returned.
#                     task.remove()
#                     
# 
#                 if command == "clone":
#                     print "Processing task - clone"
#                     # This is an acknowledgement - 
#                     # check no error returned.
#                     task.remove()
#                     
# 
#                 if command == "setting":
#                     print "Processing task - setting"
#                     # This is an acknowledgement -
#                     # check no error returned.
#                     task.remove()
# 
#                 if command == "configuration":
#                     print "Processing task - configuration"
#                     # This is another units configuration.
#                     # Get fallback IDs from response 
#                     # and update fallback GUID variable
#                     fallback_ids = task.response["common"]["configurable"]["fallback_UUIDs"]
#                     self.inputboard.update_fallback(task.from_unit, fallback_ids)
#                     task.remove()
# 
#                     # Unit specific instructions
# 
#                 if command == "output":
#                     print "Processing task - output"
#                     
#                     #Save received Memory to appropriate variable
#                     #with a timestamp.
#                     #memory = instruction
#                     self.inputboard.input_received(task)
#                     task.remove()
#                     # Set inputs to state input received
# 
# 
#                 if command == "memory":
#                     print "Processing task - memory"
#                     # This is an acknowledgement -
#                     # check no error.
#                     task.remove()
#                     raise NotImplemented
#                 
            
            
            
            # Get any announcements for input_ids
            # Need to figure out how to handle this

    def get_task(self):
        print
        print self.id, self.description
        print "get_task()"
        print "self.status",self.status

        
        # Get next message from message store for this unit’s ID
        if self.status == "new": self.new()
        if self.status == "terminated": self.terminated()
        if self.status == "waiting": self.waiting()
        if self.status == "ready": self.ready()
        
        self.process()

    def process (self):
        print "process()"
        # Generic process to be overwritten by custom 
        # processes.
        # For this process just mirror inputs to output.
        #self.get_task()

        from random import randrange
        
        self.update_memory({"dummy_reading":randrange(100)})

    def debug_unit(self):
        print "unit id:    ", self.id
        print "description:",self.description
        print "function:   ",self.function
        print "status:     ",self.status
        print
    
    

#class TypicalInputUnit(GenericUnit):
#    def process (self):
#        # self.get_task()
#      # self.update_memory(### observation/sensor data ####)
#    def unit_startup (self):
#        # Specific start-up requirements

#class TypicaProcessUnit(GenericUnit):     
#    def process (self):
#        # self.getask()
#        # if not self.taskboard.isResponse(self.set_id):
#        #     return
#      # Perform some function on 
#        # self.taskboard.response(task_id, response)
#    def unit_startup (self):
#        # Specific start-up requirements

#class TypicaOutputUnit(GenericUnit):     
#    def process (self):
#        # self.get_task()
#        # if not self.taskboard.isResponse(self.set_id):
#        #     return
#      # Perform some function on 
#        # self.taskboard.response(task_id, response)
#    def unit_startup (self):
#        # Specific start-up requirements

class MemoryUnit(GenericUnit):
    def process(self):
        # No process
        pass
    def unit_startup(self):
        # TBD
        pass
    

class ClockUnit(GenericUnit):
    def process(self):
        print "process()"
        #self.get_task()

        if self.input_poll.isTrigger():

            print "Creating a time reading"
            dt= datetime.now()
            time_stamp = dt.strftime('%Y-%m-%dT%H:%M:%S')
        
            self.update_memory({"time_stamp":time_stamp})

        
    def unit_startup(self):
        #Get NTP time
        pass

class charOutputUnit(GenericUnit):
    def process(self):
        self.get_task()
        if not self.taskboard.isResponse(self.set_id):
            item = self.memory[0]

        if self.input_poll.isTrigger():
            print self.id, "Poll Triggered",self.update_cycle
            
            print "--- 16char DISPLAY ---"
            self.memory.current_value()

    
    def unit_startup(self):
        #Get NTP time
        pass


class SimpleForecastUnit(GenericUnit):
    def process(self):
        #Make a forecast based on inputs
        pass
    def unit_startup(self):
        pass

class PassThruUnit(GenericUnit):
    def process(self):
        self.get_task()
        if not self.taskboard.isResponse(self.set_id):
            # Copy history to current memory variable.
            self.memory.history = []
            for x in self.inputboard.instances[0].history:
                self.memory.history.append(x)

            self.memory.forecast = []
            for x in self.inputboard.instances[0].forecast:
                self.memory.forecast.append(x)

    def unit_startup(self):
        pass

class AND(GenericUnit):
    def process(self):
        #self.requestinputs()
        
        pass
    def unit_startup(self):
        #Get NTP time
        pass

class OR(GenericUnit):
    pass

class NOT(GenericUnit):
    pass

class XOR(GenericUnit):
    pass

def main():  
    # Instantiate a new genericunit 
    pass
        
if __name__ == "__main__": main()
