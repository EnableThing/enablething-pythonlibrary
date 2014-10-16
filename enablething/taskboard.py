import logging
#import task
from rest import RestClient
#import taskboard_interface

class WatchedTaskBoard(object):
    def __init__(self, neighbour):
        self.url = neighbour.url
        self.unit_id = neighbour.unit_id
        self.rest = RestClient(url, unit_id)

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
        
    

    
class Taskboard(object):
    # Implement an internal task board for managing tasks, adding, removing, 
    # and requesting new tasks from primary task board.

    def __init__(self,unit_id):
        self.tasks = []  
        self.from_unit = unit_id
        self.unit_id = unit_id
        self.last_removed = None
        self.watch = Watch()
    
    def last_removed_task_id(self):
        return self.last_removed
    
    def find_task(self,task_id):
        # Returns LookupError if no tasks found.
        # Returns task object if task found.
        task = [x for x in self.tasks if x.task_id == task_id]

        if len(task) > 1:
            raise ValueError("Task lookup returned more than one task")
        if len(task) < 1:
            raise LookupError("Task lookup returned no tasks")
       
        return task[0]
    
    def isEmpty(self):
        return self.tasks == []


    def add(self, task):

        try:
            task = self.find_task(task.task_id)
        except LookupError:
            self.tasks.insert(0, task)
            return
        
        raise Exception("An existing task with that task id was found")

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

#    def request (self, to_id, command):
        # Takes a dict command and creates a new task.
        # Generate a new task with a new UUID for the task
#        task = taskobj.Task(unit_id = self.unit_id, command = command, from_unit = self.from_unit, to_unit = to_id)

#        # Add task_uuid to array live_tasks.
#        self.add(task)
#        self.status = "waiting"
#
        return task

    def respond (self, task):

        #task_id
        if task.response == {}:
            raise ValueError("Response is empty")
        
        ''' Removed this but need to think about it '''
        #task.add_response(board = 'Pending')

        #task = self.find_task(task.task_id)
        # Check this
        # http://stackoverflow.com/questions/10858575/find-object-by-its-member-inside-a-list-in-python 
        #task.update(response = task.response, board='Complete')
        #task.respond(response)
        index=-1
        for t in self.tasks:
            index=index+1
            if t.task_id == task.task_id:
                if t.response == {}:
                    print "Exisitng response is blank"
                    t = task
                    self.tasks[index] = task
                    return
                else:
                    raise LookupError("Task already has a response")
                return
            
        raise LookupError("Task lookup returned no tasks")


#     def get_new_task(self):
#         # Return 
#         for task in self.tasks:
#             if task.to_unit == self.unit_id and task.board == 'Backlog':
#                 assert(task.response == {})
#                 task.board = 'Response'
#                 return task
#                         
#         return None
    

                

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
            
