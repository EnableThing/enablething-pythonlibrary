import logging
import taskobj
import taskboard_interface

class Taskboard(object):
    # Implement an internal task board for managing tasks, adding, removing, 
    # and requesting new tasks from primary task board.

    def __init__(self,unit_id):
        self.tasks = []  
        self.from_unit = unit_id
        self.unit_id = unit_id
        self.last_removed = None
    
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
        task = taskobj.Task(unit_id = self.unit_id, command = command, from_unit = self.from_unit, to_unit = to_id)

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
                    task = taskobj.Task(unit_id = self.unit_id, **returned_task)
                    
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
            
