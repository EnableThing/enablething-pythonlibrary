#unit.py
#Unit library


import uuid
import time
import taskboard_interface
#from datetime import datetime
import json

import logging

import datetime
import time
from email import utils

import configmanage

from jsonschema import validate

# # create logger
# logger = logging.getLogger('simple_example')
# logging.setLevel(logging.DEBUG)
# 
# # create console handler and set level to debug
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# 
# # create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# 
# # add formatter to ch
# ch.setFormatter(formatter)
# 
# # add ch to logger
# logging.addHandler(ch)


# 'application' code
# logging.debug('debug message')
# logging.info('info message')
# logging.warn('warn message')
# logging.error('error message')
# logging.critical('critical message')

def create_timestamp(dt = None):
    # "local_time_rfc822":"Tue, 23 Sep 2014 18:19:54 -0700"
    if dt == None:
        nowdt = datetime.datetime.now()
    else:
        nowdt = dt
        
    nowtuple = nowdt.timetuple()
    nowtimestamp = time.mktime(nowtuple)
    utils.formatdate(nowtimestamp)
    return utils.formatdate(nowtimestamp)

def load_timestamp(timestamp):
    # from a string
    #https://gist.github.com/robertklep/2928188
    return datetime.datetime.fromtimestamp(utils.mktime_tz(utils.parsedate_tz(timestamp)))

def shortid(id):
    return id[:4] + "..."

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
    def __init__(self, data, time_stamp = None):
        if time_stamp == None:
            #time_stamp = self.create_timestamp()
            time_stamp = create_timestamp()
        self.time_stamp = time_stamp
        self.data = data
#         
#     def create_timestamp(self):
#         # "local_time_rfc822":"Tue, 23 Sep 2014 18:19:54 -0700"
#         nowdt = datetime.datetime.now()
#         nowtuple = nowdt.timetuple()
#         nowtimestamp = time.mktime(nowtuple)
#         utils.formatdate(nowtimestamp)
#         return utils.formatdate(nowtimestamp)
#         #return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
#     
    def json(self):
        # Create a dictionary
        json_dict = {
                "time_stamp":self.time_stamp,
                "data":self.data
                }
        print "DataPoint json()", json_dict
        return json_dict
    
class Memory(object):
    def __init__(self):
        self.time_range = {        
                           "past":-10000,
                           "future":10000
                           }
        self.history = []
        self.forecast = []
        self.schema = configmanage.load_schema('memoryschema.json')  


    def add(self, data, time_stamp = None):
        logging.debug("Memory add()")
        self.history.insert(0, DataPoint(data, time_stamp))

    def remove(self, datapoint):
        raise NotImplemented
        self.history.remove(datapoint)

    def validate(self, json_dict):
        return validate(json_dict, self.schema)
         
    def replace(self, json_input):
        
        self.validate(json_input)
        
        print "replace()"
        self.forecast = []
        self.history = []
        if json_input == None:
            return
        
        for f in json_input['forecast']:
            #self.forecast.append(f)
            print "    f", f['data']
            self.forecast.append(DataPoint(data = f['data'], time_stamp = f['time_stamp']))
        

        for h in json_input['history']:
            print "    h",h, h['data']
            #self.history.append(h)
            self.history.append(DataPoint(data = h['data'], time_stamp = h['time_stamp']))
        
        print "self.json()", self.json()

#     def replace_history(self, new_history):
#         raise NotImplemented("Replace existing Memory history")
#         # new_history is a json string {"point 1":{"time_stamp":time,
#         #   "datapoint":data},"point 2":{...}}

    def add_forecast(self, data, time_stamp = None):
        logging.debug("Forecast add()")
        #self.forecast.insert(0, DataPoint(data, time_stamp))
        self.forecast.append(DataPoint(data, time_stamp))


    def trim(self, low, high):
        # Provide data set from low to high only
        raise NotImplemented("Memory trim")
        memory = []
        return memory
    
    def latest(self):
        try:
            return self.history[-1]
        except: 
            return DataPoint(None, None)
    
    def json(self):
        print "memory() json()"
        # Create a dictionary
        history = []
        print "len self.history",len(self.history)
        for i in self.history:
            history.append(i.json())
        forecast = []
        print "self.forecast"
        for i in self.forecast:
            forecast.append(i.json())    
        
        json_dict = {
                "history": history,
                "forecast": forecast
                }
        print "  json_dict", json_dict
        return json_dict
    
    def debug(self):
        print self.json()
    
class Task(object):
    def __init__(self, **kwargs):

        options = {
            'task_id' : "",
            'board' : 'Backlog',
            'command' : {},
            'response' : {},
            }

        options.update(kwargs)
        
        for key, value in options.iteritems():
            setattr(self,key, value)     
        
        if self.command == "{}":
            raise Exception("Cannot create a new task with a blank command")
        
        t = self.json()
        if self.task_id == "":
            # We are creating a task that does not
            # already exists on the master board, so
            # post it and get task_id number.
            r = taskboard_interface.post_task(t)
            self.task_id = r['task_id']
        
        self.json()
        
    def command_instruction(self):

        j = self.command
   
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
            json_dict[key] = value
            setattr(self,key, value)

        self.json()

        taskboard_interface.patch_task(self.task_id,json_dict)

    def progress(self):
        self.update(board = 'In progress')
              
    def respond(self, response):
        self.update(response = response, board = 'Complete')

    def listen_for_response (self):
        #Check the message board for a command sent to task_id
        # It will be a task that is Complete
        task = taskboard_interface.get_task(self.task_id)
        print "listen_for_response() task['response']", task['response']      
        if task['response'] <> {}:
            self.update(response = task['response'])
        print "listen_for_response() self.response",self.response
    
    def isResponse(self):
        self.listen_for_response()
        if self.response == {}:
            return False
        else:
            print "Found a response!!!!"
            return True

    def print_console(self):       
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
    def debug(self):
        print "  ",self.json()
        #print "task id: ",self.task_id
        #print "board:   ", self.board
        #print "to:      ", self.to_unit
        #print "from:    ", self.from_unit
        #print "command: ", self.command
        #print "response:", self.response
        #print


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

        if len(task) > 1:
            raise LookupError("Task lookup returned more than one task")
        if len(task) < 1:
            raise LookupError("Task lookup returned no tasks")
       
        return task[0]
    
    def isEmpty(self):
        return self.tasks == []


    def add(self, task):
        self.tasks.insert(0, task)

#     def update(self, task_id):
#         task = self.find_task(task_id)
#         print "*** task.update()"
#         print "*** task.response", task.response
#         task.update()
#         print "*** task.response",task.response

    def first(self):
        # Return the first task which is a command addressed to this unit.
        
        for task in self.tasks:
            print "task_id",task.task_id
            if task.to_unit == self.from_unit:
                print task.response
                assert(task.response == {})
                return task
        return None
        
    
    def remove(self, task):
        logging.debug("Removing %s", task.task_id)
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
                    self.add(task)
                
        return new_tasks
    

                

    def listen_for_response (self, task_id):

        return self.find_task(task_id).listen_for_response()
    

    def check_all(self):
        for task in self.tasks:
            self.listen_for_response(task.task_id)
        
    def isResponse (self, task_id):

        
        return self.find_task(task_id).isResponse()

    def debug(self):
        print "taskboard", self.from_unit
        if len(self.tasks) == 0:
            print "  <No tasks on task board>"
        else:

            for t in self.tasks:
                t.debug()
            



class Input_Request(object):
    def __init__(self, task):
        self.task = task
        self.input_id = task.to_unit
        #self.id = task.task_id
        self.request_time = time.time
        self.task.response= None
        self.response_state = False

    def update(self):
        # Get latest status from public taskboard
        # and update self.*
        self.task.listen_for_response()
        print "input_request() self.response", self.task.response
        # listen_for_response updates the task entry.
        if self.task.response <> None:
            self.response_state = True
            self.response_time = time.time          

    def isResponse(self):
        return self.response_state

    def debug(self):
        print "    ", "input request", shortid(self.input_id), self.response_state, self.task.response
        

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

        #self.memory = Memory()
        
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
    def update_all(self):
        for inpt in self.requests:
            inpt.update()
            
    def debug(self):
        print "  input_set", shortid(self.id)
        for inpt in self.requests:
            inpt.debug()

class Inputs(object):
    def __init__(self, input_ids, fallback_ids):
        # Keep track of the task_id that made this request.
        # Fixed object to point to "upstream" inputs to this unit.
  
        self.input_ids = input_ids
        self.fallback_ids = fallback_ids
        
        self.input_container = []
        for i in self.input_ids:
            self.input_container.append(Memory())

        self.input_sets = []

    def __iter__(self):
        return self
    
    def next(self):
        print "next()"
        # Find first oldest input_set which
        # has a full response
        # and remove it from the input_set lists
        for input_set in self.input_sets:
            if input_set.isResponse():
                x = input_set
                self.input_sets.remove(input_set)
                print "next() input_set"
                input_set.debug()
                return x
        else:
            return None
    
    def find_set(self, set_id):
        for instance in self.input_sets:
            if set_id == instance.id:
                return instance
        raise LookupError("Set not found %s", set_id)
   
#     def process_received(self,task):
#         # Called when a response to an
#         # output task is received.  Need to find the associated input request
#         # and update it
#         # This will need to be refactored.
#         print "process received", task.task_id
#         print self.debug()
#         for instance in self.input_sets:
#             print "inputs received for task", task.task_id
#             for input_request in instance.requests:
#                 print input_request.task.task_id, task.task_id
#                 if input_request.task.task_id == task.task_id:
#                     print "Found"
#                     input_request.process_received(task)
#                     return
#         raise LookupError("Task not found in input set")
                   
    def remove_all(self):
        self.input_sets = []

    def add(self,task_set):
        i = Input_Set(task_set)
        self.input_sets.insert(0, i)
        return i

#     def remove(self, inpt):
#         self.input_sets.remove(inpt)
#         raise NotImplemented
#         #self.input_sets.remove(Input_Set())
        
    def update_all(self):
        for input_set in self.input_sets:
            input_set.update_all()
            
       
    def update_fallback(self, fallback_ids):
        raise NotImplemented
        #for instance in self.input_sets:
        #    if instance.id == input_id:
        #        instance.fallback_ids = fallback_ids
                 
    def isResponse(self, set_id = None):
        # If a set reference is provided then
        # return that set, otherwise
        # check to see if there is ANY response 
        if set_id == None:
            for input_set in self.input_sets:
                if input_set.isResponse():
                    return True
            return False           
        else:
            instance = self.find_set(set_id)
            return instance.isResponse()
    
    def debug(self):
        print "inputboard", self.id
        print "inputboard.isResponse()",self.isResponse()
        for instance in self.input_sets:
            instance.debug()          
            
class GenericUnit(object):
            
    def __init__(self,unit_config):
        self.configuration = configmanage.UnitConfiguration(unit_config)
        # consider refactor for **kwargs
        configurable = unit_config["common"]["configurable"]
        non_configurable = unit_config["common"]["non_configurable"]
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

        # load unit specific customizable variables
        specific_config = unit_config['unit_specific']['configurable']
        for key, value in specific_config.iteritems():
            setattr(self,key, value)        
        
        specific_nonconfig = unit_config['unit_specific']['non_configurable']
        for key, value in specific_nonconfig.iteritems():
            setattr(self,key, value)           

        # Additional variables
        self.status = "new"
        
        self.taskboard = Taskboard(self.id)
        self.inputboard = Inputs(self.input_ids, self.fallback_ids)
        
        self.memory =  Memory()
        
        #self.input_set = []
        #for item in self.input_ids:
        #    self.input_set.append(Memory())
        
        self.input_poll = Poll(self.update_cycle)
        # "status": [New, Ready, Running, Waiting, Terminated],

        # Run start-up
        self.set_status("new")

    def unit_startup(self):
        # Unit start-up
        # Defined by inheriting class
        pass

    def request_inputs(self):
        logging.debug("request_inputs() %s", self.inputboard.input_ids)
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
        raise NotImplemented

        # For now though, 
        self.set_status("ready")
    
    def assimilate_inputs(self, received_input_set):
        # Take inputs received from an output request and
        # address

        for request in received_input_set.requests:
            print "  reqeust.task.response", request.task.response
        
        # Add input set to fixed input_container
        print "assimilate_input() input_container, request"
        for input_container, request in zip(self.inputboard.input_container, received_input_set.requests):
            #input_container = task.response
            # Take task.response which is a json string and
            # convert it into history and forecast Memory.
            
            input_container.replace(request.task.response)
            
        # Delete input_set, no longer useful.
        # Don't need to do this because .next() already removed it
        
        # Remove associated taskboard item
        for input_container in received_input_set.requests:
            task = self.taskboard.find_task(input_container.task.task_id)
            self.taskboard.remove(task)

    def on_poll(self):
        # Request inputs at a specific interval
        if self.unit_type == "Input":
            self.process()
        else:
            self.request_inputs()
        
        self.set_status("ready")
         
        logging.debug('poll triggered')
        print "get_new_tasks", self.description

        #self.taskboard.check_all()
        # Only need to get new tasks for this unit,
        # all other tasks on our task board
        # are being addressed by this unit anyway.
        self.taskboard.get_new_tasks(self.id)


        # Update inputboard
        # We don't need to update the task board, because 
        # tasks on the task board should be things
        # for _this_ unit to action.
        self.inputboard.update_all()
        
    def ready(self):
        print self.description
        # Check if any input sets have been received
        logging.debug("Checking input sets")
#         for input_set in self.inputboard.input_sets:
#             print "set_id",input_set.id
#             print input_set.isResponse()
#             if input_set.isResponse():
#                 self.process()
        #if self.inputboard.isResponse():
          
        input_set = self.inputboard.next()
        print "ready() self.inputboard.next()", input_set

        if input_set <> None:
            print "ready() input_set <> None,", input_set
            logging.debug("input_set.requests %s %s", self.description, input_set.requests)
            print "ready() call self.assimilate_inputs(input_set)"
            self.assimilate_inputs(input_set)
            self.process()
            
        if self.input_poll.isTrigger(): 
            self.on_poll()
       

# Check for the condition where the unit’s process
# hasn’t been able to run because not all 
# information received.

       

        # Get next message from message store for this unit’s GUID
        # Unit is ‘ready’ so it is ready to process a received command.
              
        #if len(self.taskboard.tasks) > 0:
        print self.taskboard.debug()
        
        # This next function returns the next task
        # which is a command addressed to this unit.
        # not a response
        # So we look for the task.to_unit to equal our units address.
        
        task = self.taskboard.first()
        print "task", task
        if task <> None:
            assert (self.id == task.to_unit)
            # There are tasks waiting to be processed
            # Pop the earliest task and process it
            # task = self.taskboard.first()
            logging.info("json of task being processed %s", task.json())

            command = task.command.keys()[0]
            instruction = task.command.get(command)
                
            if command == "announce":
                logging.debug("Command received - announce")
                #State this devices GUID and fallback GUIDs
                task.respond({"fallback_ids":self.fallback_ids})
                self.taskboard.remove(task)
    
            if command == "start":
                logging.debug("Command received - start")
                # Start this device
                # No action, device is already running.
                task.respond({"status":self.set_status})
                #t = task.task_id
                #self.taskboard.find_task(t)
                
                self.taskboard.remove(task)
                #print "Need to confirm task removed"
                #self.taskboard.find_task(t)
    
            if command == "terminate":
                logging.debug("Command received - terminate")
                # Organization chart process will handle
                # this, as will fall-back 
                # process in other units.
                self.set_status("terminated")
                task.respond({"status":self.set_status})
                self.taskboard.remove(task)
    
    
            if command ==  "clone":
                logging.debug("Command received - clone")
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
                logging.debug("Command received - setting")
                # Change configuration of this unit
                # Update configuration in persistent
                # memory to received setting
                self.configuration.patch(instruction)
                self.taskboard.remove(task)                    
                self.set_status("new")

            if command == "configuration":
                logging.debug("Command received - configuration")               
                # Respond with this units configuration
                task.respond(self.configuration.unit_config)
                self.set_status("ready")
    
            if command == "output": 
                logging.debug("Command received - output")
                # respond with Memory ie (horizon) history and forecast
                # Provides Memory of output
                task.respond(self.memory.json())
                self.taskboard.remove(task)
                self.set_status("ready")
                
            if command == "memory":
                logging.debug("Command received - memory")
                # Overwrite units Memory ie (horizon) history and forecast
                # This is typically used to update memory variable so is common
                # to all devices.  If it is a memory unit the memory is updated, for
                # other units it resets the unit memory.             
                self.memory.replace(instruction)
                self.taskboard.remove(task)
                        
            
            # Get any announcements for input_ids
            # Need to figure out how to handle this

    def get_task(self):

        logging.info("get_task %s", self.description)
        logging.debug("get_task() - status %s", self.status)
        # Get next message from message store for this unit’s ID
        if self.status == "new": self.new()
        if self.status == "terminated": self.terminated()
        if self.status == "waiting": self.waiting()
        if self.status == "ready": self.ready()
        
        
        #self.process()

    def process (self):
        logging.info("process() %s", self.description)
        # Generic process to be overwritten by custom 
        # processes.
        # For this process just mirror inputs to output.
        #self.get_task()

        from random import randrange
        
        self.memory.add({"dummy_reading":randrange(100)})

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
        logging.info("process() %s", self.description)
        
        #dt= datetime.now()
        #time_stamp = dt.strftime('%Y-%m-%dT%H:%M:%S')
        time_stamp = create_timestamp()
        self.memory.add({"time":time_stamp})
        
    def unit_startup(self):
        #Get NTP time
        pass



class SimpleForecastUnit(GenericUnit):
    def process(self):
        print "PassThruUnit process()"
        # For the PassThruUnit take the latest received memory and make the units
        # memory reflect this.
        # Raise an exception if there is more than one input
        
        # Get the next completed input set
        logging.info("start process() %s", self.description)
        
        ''' Take last value and forecast this out for an hour '''

        logging.debug("Passing input to memory")

        if len(self.inputboard.input_container) > 1:
            raise Exception("More than one input passed to ForecastUnit.")
        
        self.memory.history = self.inputboard.input_container[0].history
        self.memory.forecast = self.inputboard.input_container[0].forecast


        # See if there is any data to extrapolate 
        try:
            data = self.memory.history[0].data
            start_time = load_timestamp(self.memory.history[0].time_stamp)
        except IndexError:
            data = None
            start_time = datetime.datetime.now()

        if self.update_cycle <= 0:
            delta_t = 60*5    
        else:
            delta_t = self.update_cycle
        print "data", data
        
        self.memory.forecast = []
        for i in xrange(10):
            ts = start_time + datetime.timedelta(seconds = i * delta_t)            
            time_stamp = create_timestamp(ts)
            self.memory.add_forecast(data, time_stamp)        
  
    def unit_startup(self):
        pass

class PassThruUnit(GenericUnit):
    def process(self):
        print "PassThruUnit process()"
        # For the PassThruUnit take the latest received memory and make the units
        # memory reflect this.
        # Raise an exception if there is more than one input
        
        # Get the next completed input set
        logging.info("start process() %s", self.description)
        
        
        if len(self.inputboard.input_container) > 1:
            raise Exception("More than one input passed to PassThruUnit.")

        logging.debug("Passing input to memory")
        print "self.inputboard.input_container[0].history"
        print self.inputboard.input_container[0].history
        
        self.memory.history = self.inputboard.input_container[0].history
        self.memory.forecast = self.inputboard.input_container[0].forecast
  

    def unit_startup(self):
        pass

class NullUnit(GenericUnit):
    def process(self):
        print "NullUnit process()"
        raise NotImplemented
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
