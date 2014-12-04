import logging
import time
#import task
from rest import RequestHandler
from enablethingexceptions import TaskError, TaskboardError

import copy

class WatchedTaskBoard(object):
    def __init__(self, neighbour):
        self.url = neighbour.url
        self.unit_id = neighbour.unit_id
        self.rest = RequestHandler(url, unit_id)

class Watch(object):
    def __init__(self):
        
        self.watched_taskboards = []
        
    def add_taskboard(self,neighbour):
        # neighbour is a class containing information about the
        # neighbour, including the url and unit_id
        
        self.watched_taskboards.append(WatchedTaskBoard(neighbour))
    
    def get_new_responses(self):
        for watched_taskboard in self.watch_taskboards:
            watched_taskboard.rest.get_new_commands()
            watched_taskboard.rest.get_new_responses()
    
    def remove_taskboard(self):
        raise NotImplemented


class TaskSet(object):
    def __init__(self,tasks):
        self.tasks = tasks
    def isResponse(self):
        for task in self.tasks:
            if not task.isResponse():
                return False
        return True

    
class Taskboard(object):
    # Implement an internal task board for managing tasks, adding, removing, 
    # and requesting new tasks from primary task board.

    def __init__(self,unit_id, description, debug = True):
        self.debugFlag = debug
        self.description = description
        self.tasks = []
        self.tasksets = []  
        self.from_unit = unit_id
        self.unit_id = unit_id
        self.last_removed = None
        self.watch = Watch()
        self.current_task = 0
        self.num_removed =0
        self.removed_tasks = []
        self.index = 0

    
    def find_task(self,task_id):
        # Returns LookupError if no tasks found.
        # Returns task object if task found.
        task = [x for x in self.tasks if x.task_id == task_id]

        if len(task) > 1:
            for t in task:
                t.debug()
            raise ValueError("Task lookup returned more than one task")
        if len(task) < 1:
            
            #self.debug()
            raise LookupError("Task lookup returned no tasks")
       
        return task[0]

    def queue(self, task):
        # Ensure "processed" flag is false
        task.processed = False
        self.index = self.index+1
        logging.info("Queueing task %s to unit %s on %s", task.task_id[:4],  self.unit_id[:4], self.description)
        try:
            existing_task = self.find_task(task.task_id)
            
        except LookupError:
            # Task is not found so add a new task
            if task.isResponse():
                task.response_timestamp = time.time()
            elif task.isCommand():
                task.command_timestamp = time.time()
            task.index = self.index
            self.tasks.append(task)
            return
        
        if existing_task.isResponse():
            logging.info("Existing task %s has a response.  Task not addeded to queue.", task.task_id[:4])
            return   
        elif existing_task.isCommand():
            
            for index, t in enumerate(self.tasks):            
                if t.task_id == task.task_id:
            
                    if t.isResponse():
                        
                        raise LookupError("Task already has a response")
                    elif t.isCommand() and not t.isResponse() and task.isResponse():
                        logging.debug("Existing response is blank %s", task.task_id)   
            
                    
                        task.response_timestamp = time.time()
                        task.index = self.index
                        self.tasks[index] = task
            
                        existing_task.note = "Task replaced"
                        logging.info("Task %s replaced", task.task_id[:4])
                        return
                    else:
                        logging.error("Task %s attempted replace of identical task.  No action.", task.task_id[:4])
                        
                        return
            
            raise LookupError("Task lookup returned no matching tasks")
        
        raise Exception ("Undefined situtation")
        
    def __iter__(self):
        return self

    def next(self): # Python 3: def __next__(self)
        #print "next()"
        #if len(self.tasks) > 0:
        #    return self.tasks[0]
        #else:
        #    return None
        
        for task in self.tasks:
            self.demote(task)
            #print task.debug()
            if not task.processed:
                #print ">", task.debug()
                return task
            
        return None
                   
    
    def dequeue(self, task, protect_tasksets = True):
        
        logging.info("Dequeue() task %s from unit %s on %s", task.task_id[:4],  self.unit_id[:4], self.description)
        self.last_removed = task.task_id
               
        for existing_task in list(self.tasks):
            if task.task_id == existing_task.task_id:
                #if self.debugFlag:
                self.removed_tasks.append(existing_task) 
                self.tasks.remove(existing_task)
                logging.info("Dequeued task %s from unit %s on %s", task.task_id[:4],  self.unit_id[:4], self.description)
                self.num_removed += 1
                return
        raise TaskboardError("Unable to dequeue task")
        

    
    def demote(self,movetask):
        try:
            found_task = self.find_task(movetask.task_id)
        except LookupError:
            raise LookupError("Request task for demotion not found")
            
        for i, task in enumerate(self.tasks):
            if task.task_id == movetask.task_id:
                index = i
                break
        #print "index", index
        self.tasks.insert(len(self.tasks), self.tasks.pop(index))
    
    def make_first(self,movetask):
        try:
            found_task = self.find_task(movetask.task_id)
        except LookupError:
            pass
        for i, task in enumerate(self.tasks):
            if task.task_id == movetask.task_id:
                index = i
                break
        #print "index", index
        self.tasks.insert(0, self.tasks.pop(index))

                       
    def isResponse (self, task_id):

        
        return self.find_task(task_id).isResponse()

    def debug(self, onlyerrors = False):
        print "="*79
        print "Taskboard", self.unit_id[:4]+ " " +self.description,
        r = 0
        c=0
        for i in self.tasks:
            if i.isResponse():
                r = r + 1
            elif i.isCommand() and i.isResponse():
                c = c + 1
            
        
        if len(self.tasks) == 0 and len(self.removed_tasks) ==0:
            print "  <No tasks on task board>"

        else:
            print
            print "<", len(self.tasks), "tasks on task board (", self.num_removed, "removed)>"
            print "  Responses",r,"/ Commands:",c
            print "  unit  task Age(ms)   from  to      command response"
            print "  live"
            for t in self.tasks:
                t.debug()
            print "  completed/removed"
            for t in self.removed_tasks:
                if onlyerrors:
                    if t.status != 'Completed':
                        t.debug()
                else:
                    t.debug()
                
                 
        print "="*79

    def debug_tasksets(self):
        print "Tasksets, number removed: ",self.num_removed
        for taskset in self.tasksets:
            print taskset.isResponse(), 
            for task in taskset.tasks:
                print task.task_id[:4],
                        

    def add_taskset(self, tasks):
        self.tasksets.append(TaskSet(tasks))
    
    def next_taskset(self):
        
        for taskset in list(self.tasksets):
            isresponse = True
            collection = []
            for task in list(taskset.tasks):
            
                found_task = self.find_task(task.task_id)

                collection.append(found_task)
                if not found_task.isResponse():
                    isresponse = False
                    
            if isresponse == True:
                # A response taskset has been found
                for task in taskset.tasks:
                        found_task = self.find_task(task.task_id)
                        self.dequeue(found_task, protect_tasksets = False)                      
                self.tasksets.remove(taskset)
                
                return collection
            
        return None
                

