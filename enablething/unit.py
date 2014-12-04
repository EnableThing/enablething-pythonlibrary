#unit.py
#Unit library
import requests
import json
import uuid
import re
import logging
import datetime
import time

import config
import rest
from task import Task, Memory
from taskboard import Taskboard
#from router import RouterHandler
from enablethingexceptions import TaskError, RouterError
from jsonschema import ValidationError
#from datetime import datetime



#from email import utils
from jsonschema import validate

from collections import defaultdict, OrderedDict
from restlite import restlite



def shortid(id):
    if id == None:
        return "----"
    else:
        return id[:4] + "..."

class Statistics(object):
    def __init__(self):
        self.TxTasks = 0 # Number of tasks transmitted by the unit
        self.RxTasks = 0 # Number of tasks received by the unit
        self.uptime = 0  # The time elapsed since last reset
        self.posts = 0 # Number of POST requests
        self.gets= 0 # Number of GET requests 
    def update(self):
        pass
        

class Unit(object):
    def __init__(self, ip, port, unit_id, fallback_units):
        self.unit_id = unit_id
        logging.debug("Unit __init__() %s", unit_id)
        
        self.last_contact = None
        self.last_seen_by = None
        self.fallback_units = fallback_units
        
        self.rest = rest.RequestHandler(ip, port, self)
        self.stats = Statistics()
        #self.posts = 0
        #self.gets = 0

    def shortid(id):
        if id == None:
            return "----"
        else:
            return id[:4] + "..."
    
    def update(self):
        self.last_contact = time.time()
    
    def _process_json_tasks(self, json_tasks, response = False):
        logging.debug("_process_json_tasks()")
        tasks = []
        for json_task in json_tasks:
            task = Task(self.unit_id, json_task)
            if response == True and task.response == {}:
                # Do not add task if there is not a response
                pass
            else:
                tasks.append(task)
            
        return tasks
        
    def add_fallback_unit(self, fallback_unit):
        self.fallback_units.append(fallback_unit)
        
    def post_task(self, task):
        logging.info("unit() post_task() %s to  %s", task.task_id[:4], self.unit_id[:4])
        #assert(isinstance(task, Task))
        logging.info("Chronicle before %s", task.chronicle)
        print "task.chronicle",task.chronicle
        task.close_chronicle()
        logging.info("Chronicle after %s", task.chronicle)
        self.rest.post(self.unit_id, task.json())
        
        self.stats.posts += 1
        
        self.last_contact = time.time()

    def get_new_responses(self):
        tasks_dict = self.rest.get(self.unit_id+"/tasks?response")
        self.stats.gets += 1
        tasks = []
        for task_dict in tasks_dict:
            try:
                task = Task(self.unit_id, **tasks_dict[task_dict])
                if task.response <> {}:
                    tasks.append(task)
            except TaskError:
                pass
            
        self.last_contact = time.time()
        return tasks
    
    def get_new_commands(self):
        tasks_dict = self.rest.get(self.unit_id+"/tasks?command")
        self.stats.gets += 1
        tasks = []
        for task_dict in tasks_dict:
            try:
                task = Task(self.unit_id, **tasks_dict[task_dict])
            
                if task.response == {}:
                    tasks.append(task)
            except TaskError:
                pass
            
        self.last_contact = time.time()
        return tasks
    
    def get_response(self, task = None):
        #assert(isinstance(task, Task))
        task_dict = self.rest.get(self.unit_id +"/task/" + task.task_id)
        self.stats.gets += 1
        try:
            print "task_dict", task_dict
            task = Task(self.unit_id, **task_dict)
        except ValueError:
            return None
        except TaskError:
            return None

        self.last_contact = time.time()
  
        return task

class NeighbourUnit(Unit):
    def __init__(self, ip, port, unit_id, fallback_units, home_unit_id):
        
        Unit.__init__(self, ip, port, unit_id, fallback_units)
        self.destination_goodness = {}
        self.watch = False
        self.post_capable = False
        
        self.home_unit_id = home_unit_id
    
        
    def add_destination(self, destination):
        if self.unit_id == destination or self.home_unit_id == destination:
            return
        try:
            self.destination_goodness[destination]
            # Do nothing.  Destination already exists
        except KeyError:
            self.destination_goodness[destination] = 0
         
        
            
        


class InputUnit(Unit):
    def __init__(self, ip, port, unit_id, fallback_units):
        Unit.__init__(self, ip, port, unit_id, fallback_units)
        self.memory = Memory()
    def debug(self):
        print self.unit_id, "forecast"
        for datapoint in self.memory.forecast:
            print datapoint.time_stamp, datapoint.data
        print self.unit_id,"history"
        for datapoint in self.memory.history:
            print datapoint.time_stamp, datapoint.data
        


    

 
def main():  
    # Instantiate a new genericunit 
    pass
        
if __name__ == "__main__": main()
