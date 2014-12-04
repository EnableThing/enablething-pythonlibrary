#unit.py
#Unit library
import requests
import json
import uuid
import re
import logging
import datetime
import time

from unit import InputUnit, NeighbourUnit
import config
import rest
from task import Task, Memory
from taskboard import Taskboard
from router import RouterHandler
from enablethingexceptions import TaskError, RouterError
#from datetime import datetime



#from email import utils
from jsonschema import validate

from collections import defaultdict, OrderedDict
from restlite import restlite



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


        


    

    
    
class InputConnector(object):
    def __init__(self, unit_id, input_ids, fallback_ids):
        self.unit_id = unit_id
        # Keep track of the task_id that made this request.
        # Fixed object to point to "upstream" inputs to this unit.
  
        #self.input_ids = input_ids
        self.inputunits = []
        ip = "127.0.0.1"
        port = 8080
        for input_id in input_ids:
            self.inputunits.append(InputUnit(ip, port, input_id, []))
                
        self.fallback_ids = fallback_ids
        

    def add_inputunit(self, inputunit):
        self.inputunits.append(inputunit)

                            
    
    def debug(self):
        logging.debug("inputboard %s", self.unit_id)
        logging.debug("inputboard isResponse %s", self.isResponse())
        for instance in self.input_sets:
            instance.debug()          


            
class Controller(object):
    def _set_status(self, state):
        valid_states = {"new", "terminated", "waiting", "ready"}
        if 'new' not in valid_states:
            raise Exception
        self.status = state
 
    def controller_update(self):
        logging.debug("controller_update()")
        logging.debug("get_task %s", self.description)
        logging.debug("get_task() - status %s", self.status)

        #Get next message from message store for this unit's ID
        if self.status == "new": self._new()
        if self.status == "terminated": self._terminated()
        if self.status == "waiting": self._waiting()
        if self.status == "ready": self._ready()
   
    def _on_poll(self):
        logging.debug("on_poll()")
        # Request inputs at a specific interval
        if self.unit_type == "Input":
            self.process()
        
        print "processing subscriptions"
        new_tasks = self.router.subscriptions.get_new_tasks()
        for task in new_tasks:
            #task.debug()
            #print task
            try:
                self.router.received.queue(task)

            except LookupError:
                # Existing task in the database
                pass
        
        print "Requesting inputs", self.unit_id[:4]
        self.request_inputs()
        
        self._set_status("ready")
        
        

        # Only need to get new tasks for this unit,
        # these are added to the taskboard
        # and then processed by another part of the application

   
    def unit_startup(self):
        pass
   
    def process(self):
        logging.info("Empty process called")
        pass
    
    def setup(self):
        pass
    def _process_command(self, task):
        logging.info("_process_command()")
        # Task is a command to this unit, needing a response from this unit.
        #assert (self.unit_id == task.to_unit)

        command = task.command.keys()[0]
        instruction = task.command.get(command)
        
        logging.info("Unit %s processing command %s",self.unit_id, command)
        if self.unit_id == task.from_unit:
            # The is a command starting at originating unit, needing to be forwarded.
            task.note = "Task put on TX queue"    
        elif self.unit_id == task.to_unit:
            if command == "announce":
                #State this devices GUID and fallback GUIDs
                task.add_response(response = {"fallback_ids":self.fallback_ids})         
            elif command == "start":
                # Start this device
                # No action, device is already running.
                task.add_response(response = {"status":self._set_status})  
            elif command == "terminate":
                # Organization chart process will handle
                # this, as will fall-back 
                # process in other units.
                self._set_status("terminated")
                task.add_response(response = {"status":self._set_status})
            elif command ==  "clone":
                # if possible, create a copy of this unit
                # with a new UUID
                # not possible for hardware units
                response = {"success":False,
                            "unit_id":None}
                task.add_response(response = response) 
            elif command == "setting":
                # Change configuration of this unit
                # Update configuration in persistent
                # memory to received setting
                self.configuration.patch(instruction)
                response = {"success":True}
                task.add_response(response = response)
            elif command == "configuration":
                # Respond with this units configuration
                task.add_response(response = self.configuration.unit_config)
            elif command == "output": 
                # respond with Memory ie (horizon) history and forecast.  Provides Memory of output
                task.add_response(response = self.memory.json())
            elif command == "memory":
                logging.debug("Command received - memory")
                # Overwrite units Memory ie (horizon) history and forecast
                # This is typically used to update memory variable so is common
                # to all devices.  If it is a memory unit the memory is updated, for
                # other units it resets the unit memory.             
                self.memory.replace(instruction)
                response = {"success":True}
                task.add_response(response = response)
            else:
                raise Exception("Unrecognized command")
            
            self._set_status("ready")
            
            task.note = "Processed by to_unit"
            
            assert(task.isResponse() == True)
        else:
            logging.critical("Task %s has no determined action from unit %s", task.task_id[:4], self.unit_id[:4]) 
            logging.info("Task %s isResponse %s isCommand %s",task.task_id[:4], task.isResponse(), task.isCommand()) 
            logging.info("self.unit_id %s from %s to %s",self.unit_id[:4],  task.from_unit[:4], task.to_unit[:4])
            raise Exception("Undetermined action ... needs to be addressed")
        
        self.router.transmit.queue(task)
        logging.info("Unit %s task %s queued on TX queue",self.unit_id[:4], task.task_id[:4])
               

        
        #self.taskboard.dequeue(task)       
 
    def _process_response(self,task):
        logging.info("_process_response()")
        
        command = task.command.keys()[0]
        response = task.response
        
        logging.info("Process a %s response to unit %s", command, self.unit_id[:4])
        
        logging.info("Process a %s response to unit %s", command, self.unit_id[:4])

        if self.unit_id == task.to_unit:
            # This is a response at the destination unit, needed to be sent back.
            task.note = "response forwarded"           
            self.router.transmit.queue(task)
            
        elif self.unit_id == task.from_unit:
            if command == "announce":
                logging.info("Response received - announce")
                print "Need to implemented announce receiving"
    
            elif command == "start":
                logging.debug("Response received - start")
    
    
            elif command == "terminate":
                logging.debug("Response received - terminate")
    
            elif command ==  "clone":
                logging.debug("Response received - clone")
                
            elif command == "setting":
                logging.debug("Response received - setting")
                
            elif command == "configuration":
                logging.debug("Response received - configuration")
                
            elif command == "output":
                # An "output" response has been received so 
                # check whether any of the tasksets is now complete. 
                logging.info("Response received - output")
    
                for inputunit in self.inputconnector.inputunits:
                    if task.to_unit == inputunit.unit_id:
                        logging.debug("adding input from %s", shortid(task.to_unit))
                        logging.debug("task.response %s", task.response)   
                        inputunit.memory.replace(task.response) 
    
                 
            elif command == "memory":
                logging.debug("Response received - memory")
                task.status = "Completed"
    
            else:       
                raise Exception("Invalid command received", task.command)
        else:
            logging.critical("Task %s is neither Response nor Command unit %s", task.task_id[:4], self.unit_id[:4]) 
            logging.info("Task %s isResponse %s isCommand %s",task.task_id[:4], task.isResponse(), task.isCommand()) 
            logging.info("self.unit_id %s from %s to %s",self.unit_id[:4],  task.from_unit[:4], task.to_unit[:4])
            raise Exception("Not response or command")
            
            
        task.note = "Unit added response"
        task.status = "Completed"
            
        self.router.subscriptions.unsubscribe_task(task)
            
          
        self.taskboard.dequeue(task)
        logging.info("self.taskboard.dequeue %s", self.unit_id[:4])

        
    def process_task(self, task):
        logging.info("process_task()")
        # The only tasks on the taskboard should be 
        # (a) commands for this unit
        # (b) responses for this unit
        # Anything else should raise an exception 

    
        if task.send_retries >= self.max_send_retries:
            task.note = "Retries exceeded"
            self.taskboard.dequeue(task)
            return
        
        if time.time() - task.processed_time < self.task_timeout:
            print "timeout", time.time(), task.processed_time, time.time() - task.processed_time, self.task_timeout   
            return
            
#         if task.processed:
#             if task.send_retries >= self.max_send_retries:
#                 raise Exception
#                 task.note = "Retries exceeded"
#                 self.taskboard.dequeue(task)
#                 return
#             else:
#                 logging.info("self.task_timeout %s", self.task_timeout)
#                 
#                 if task.processed_time - time.time() < self.task_timeout:
#                     return
                       
        task.processed = True
        task.processed_time = time.time()
        task.send_retries += 1

        if task.previous_neighbour == self.unit_id:
            raise TaskError("Attempting to route to self " + self.unit_id[:4])
            return
        elif task.isResponse():   
            # This is a response received back at originating unit
            task.note = "process response"       
            self._process_response(task)
        elif task.isCommand():
            # This is a command received at the destination unit
            task.note = "Task put on TX queue"
            self._process_command(task)            
        else:    
            logging.critical("Task %s has no determined action from unit %s", task.task_id[:4], self.unit_id[:4]) 
            logging.info("Task %s isResponse %s isCommand %s",task.task_id[:4], task.isResponse(), task.isCommand()) 
            logging.info("self.unit_id %s from %s to %s",self.unit_id[:4],  task.from_unit[:4], task.to_unit[:4])
            raise Exception("Undetermined action ... needs to be addressed")
             

       
    def _new(self):
        logging.info("_new()") 
        
        # Send an announce to all known neightbours
        for neighbour in self.router.neighbours:

            task = Task(self.unit_id, 
                        from_unit = self.unit_id, 
                        to_unit = neighbour.unit_id, 
                        command = {"announce":{"fallback_ids":self.fallback_ids}})
            task.note = "Unit created task"

            self.taskboard.queue(task)
            self.taskboard.debug()
            
        self.unit_startup()
        self._set_status("ready")
 
    def _ready(self):
        # Check if any input sets have been received
        logging.info("_ready() %s", self.description)
        
        self.router.update_router()        
        self.process()
        
        self.taskboard.debug()
             
        if self.input_poll.isTrigger():
            logging.info("_ready() poll triggered") 
            self._on_poll()
            logging.info("_ready() poll completed") 

        # Get next message from message store for this unit's GUID
        # Unit is 'ready' so it is ready to process a received command.

        task = self.taskboard.next()
               
        if task is None:
            logging.info("No task retrieved")
            return

        
        if task.current_hop == self.unit_id:
            logging.info("Task %s already forwarded", task.task_id[:4])
            raise Exception

        self.process_task(task)
       
      
    def _terminated(self):
        # Listen for a possible command to re-start the unit.
        task = self.listen_for_unitID(self.id)
 
        if task.command == "start":
            newtask = self.taskboard.request(self.id, task.command)
 
        self._set_status("ready")
 
    def _waiting(self):
        # Device didn't update last cycle, so unit
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
        self._set_status("ready")  
         
    def request_inputs(self):
        logging.info("request_inputs()")
        logging.debug("%s unit %s request inputs", self.function, shortid(self.unit_id))
        
        if self.inputconnector.inputunits == None:
            logging.info("self.inputconnector.inputunits == None")
            return
        
        tasks = [] 
        for inputunit in self.inputconnector.inputunits:
            print "inputunit", inputunit.unit_id

            task = Task(self.unit_id, 
                        to_unit = inputunit.unit_id, 
                        from_unit = self.unit_id,
                        command = {"output":{}}) 
            #self.router.transmit.queue(task)
            self.taskboard.queue(task)
            
            tasks.append(task)
                       
        self.taskboard.add_taskset(tasks)
        x=[]
        for t in tasks:
            x.append(t.task_id[:4])
        logging.info("New taskset created: %s", x)
                 
            
class BaseUnit(Controller):
            
    def __init__(self, url, unit_config):
        self.url = url
        
        self.max_send_retries = 3
        self.task_timeout = 90 # Timeout in s
        
        self.configuration = config.UnitConfiguration(unit_config)
        # consider refactor for **kwargs
        configurable = unit_config["common"]["configurable"]
        non_configurable = unit_config["common"]["non_configurable"]
        self.json_config = unit_config

        # Apply configuration
        #self.id = non_configurable["unit_id"]
        self.unit_id = non_configurable["unit_id"]

        self.function = non_configurable["function"]
        self.description = non_configurable["description"]

        
        
        self.fallback_ids = configurable["fallback_UUIDs"]
        
        self.input_ids = configurable["input_UUIDs"]
        
        self.inputconnector = InputConnector(self.unit_id, self.input_ids, self.fallback_ids)
        
        #self.inputconnector.inputunits = []
        #for input_id in self.input_ids:
        #    ip = "127.0.0.1"
        #    self.inputconnector.inputunits.append(InputUnit(ip, input_id, []))

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
        
        #self.tasksethandler = TaskSetHandler()
        
        #self.taskboard = taskboardobj.Taskboard(self.id)
        self.taskboard = Taskboard(self.unit_id, 'Taskboard') 
        

        
        neighbour_ids = configurable["neighbours"]
        
        print "neighbour_ids", neighbour_ids
        

        
        neighbours = []
        for neighbour_id in neighbour_ids:
            # ip, unit_id, fallback_units
            ip = "127.0.0.1"
            port = 8080
            
            if neighbour_id != self.unit_id:
                neighbours.append(NeighbourUnit(ip, port, neighbour_id,[], self.unit_id))
            
        
        self.router = RouterHandler(self.unit_id, self.taskboard, neighbours)    
        
        for neighbour in self.router.neighbours:
            neighbour.add_destination(neighbour.unit_id)
              
        
        
#         self.router.unit_mapper = {}
#         for unit in self.router.neighbours:
#             self.router.unit_mapper[unit.id] = unit
#         for unit in self.inputconnector.inputunits:
#             # This will override existing values,
#             # which is fine because the inputconnector is what we want.
#             self.router.unit_mapper[unit.id] = unit
            
        self.rest = rest.RestServer(self.unit_id, self.taskboard, self.router)
        #self.router.subscriptions = Subscriptions()
        
        self.memory = Memory()
        
        self.task = None
           
        self.input_poll = Poll(self.update_cycle)
        # "status": [New, Ready, Running, Waiting, Terminated],

        # Run start-up
        self._set_status("new")
        logging.info("Unit successfully configured")
        


    
    def assimilate_inputs(self, task_set):
        logging.debug("%s unit %s assimilate inputs", self.function, shortid(self.unit_id))
        # Take inputs received from an output request and
        # place in input unit memory.            
        for inputunit in self.inputconnector.inputunits:
            for task in task_set:
                if task.to_unit == inputunit.unit_id:
                    logging.debug("adding input from %s", shortid(task.to_unit))
                    logging.debug("task.response %s", task.response)
                    
                    inputunit.memory.replace(task.response)    
            
        # Remove tasks from taskboard    
        for task in task_set:
            print "assimilate inputs ... removing task", task.task_id[:4]
            task.note = "Inputs assimilated by unit"
            self.taskboard.dequeue(task)
            



        


    def debug_unit(self):
        logging.debug("unit id:     %s", self.id)
        logging.debug("description: %s", self.description)
        logging.debug("function:    %s", self.function)
        logging.debug("status:      %s", self.status)
        

def main():  
    # Instantiate a new genericunit 
    pass
        
if __name__ == "__main__": main()
