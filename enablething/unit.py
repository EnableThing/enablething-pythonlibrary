﻿#unit.py
#Unit library


import uuid

import configmanage
#import taskboard_interface
import taskobj
import taskboardobj
import router
#from datetime import datetime
#import json

import logging

import datetime
import time
#from email import utils
#from jsonschema import validate

from collections import defaultdict, OrderedDict


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
            self.input_container.append(taskobj.Memory())

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
        
        self.taskboard = taskboardobj.Taskboard(self.id)
        self.inputboard = Inputs(self.input_ids, self.fallback_ids)
        
        self.memory =  taskobj.Memory()
        
        self.router = router.Router(self.id)
        
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
                
                self.taskboard.remove(task)

    
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
        time_stamp = taskobj.create_timestamp()
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
            start_time = taskobj.load_timestamp(self.memory.history[0].time_stamp)
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
            time_stamp = taskobj.create_timestamp(ts)
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
