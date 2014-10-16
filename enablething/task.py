
import time
import datetime
from email import utils
import uuid
import logging

from jsonschema import validate, ValidationError
import jsonschema

import config

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

class DataPoint(object):
    def __init__(self, data, time_stamp = None):
        if time_stamp == None:
            #time_stamp = self.create_timestamp()
            time_stamp = create_timestamp()
        self.time_stamp = time_stamp
        self.data = data
     
    def json(self):
        # Create a dictionary
        json_dict = {
                "time_stamp":self.time_stamp,
                "data":self.data
                }
        return json_dict
    
class Memory(object):
    def __init__(self):
        self.time_range = {        
                           "past":-10000,
                           "future":10000
                           }
        self.history = []
        self.forecast = []
        self.schema = config.load_schema('schema/memoryschema.json')  


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

        self.forecast = []
        self.history = []
        if json_input == None:
            return
        
        for f in json_input['forecast']:
            #self.forecast.append(f)
            self.forecast.append(DataPoint(data = f['data'], time_stamp = f['time_stamp']))
        

        for h in json_input['history']:
            #self.history.append(h)
            self.history.append(DataPoint(data = h['data'], time_stamp = h['time_stamp']))


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
        # Create a dictionary
        history = []
        for i in self.history:
            history.append(i.json())
        forecast = []
        for i in self.forecast:
            forecast.append(i.json())    
        
        json_dict = {
                "history": history,
                "forecast": forecast
                }

        return json_dict
    
    def debug(self):
        print self.json()



class Chronicle(object):
    # Class to extract and write chronicle to message
    def __init__(self):
        self.chronicle_start_time = time.time()

    def _subfinder(self,mylist, pattern):
        #http://stackoverflow.com/questions/10106901/elegant-find-sub-list-in-list
        matches = []
        for i in range(len(mylist)):
            if mylist[i] == pattern[0] and mylist[i:i+len(pattern)] == pattern:
                matches.append(pattern)
        return matches
 
    def _longestrun(self, myList):
        for n in xrange(2, len(myList)):
            pattern = myList[-n:]
            if len(self._subfinder(myList, pattern)) > 1:
                return True
        return False
               
    def isLoop(self):
        units = []
        for chronicle in self.chronicle: 
            units.append(chronicle['unit_id'])
        return self._longestrun(units)

    def find_units(self):
        self.visited_uuids = []
        for chronicle in self.chronicle:
            visited_uuid = chronicle['unit_id']
            if visited_uuid <> self.unit_id:
                self.visited_uuids.append(visited_uuid)
        return self.visited_uuids

    def _current_hop(self):
        hop = 0
        for chronicle in self.chronicle:
            if self.unit_id == chronicle['unit_id']:
                if chronicle['hop'] > hop:
                    hop = chronicle['hop']
        if hop == 0:
            raise LookupError("UUID not found")     
        return hop
        
    def next_neighbour(self):
        neighbour = None
        hop = self._current_hop()
        # The hop we need is the next one
        hop = hop + 1
        if hop > len(self.chronicle):
            raise LookupError("Last unit")
        
        for chronicle in reversed(self.chronicle):
            if chronicle['hop'] == hop:
                neighbour = chronicle['unit_id']
                return neighbour
    
    def previous_neighbour(self):
        neighbour = None
        hop = self._current_hop()
        # The hop we need is the previous one
        hop = hop - 1
        if hop == 0:
            raise LookupError("First unit provided as lookup value")
        for chronicle in reversed(self.chronicle):
            if chronicle['hop'] == hop:
                neighbour = chronicle['unit_id']
                return neighbour
                
    def add_chronicle(self):
        elapsed_time = time.time() - self.chronicle_start_time     
        hops = len(self.chronicle)
        self.chronicle.append({"hop":hops + 1, "unit_id": self.unit_id, "time_ms": 1000*round(elapsed_time,3)})   

    def cost(self):
        # Calculate "cost" of the chronicle record
        cost = 0
        for item in self.chronicle:
            cost = cost + item['time_ms']
        return cost

    def validate_chronicle(self):
        # Check for non-unique hop count
        hops = []
        for chronicle in self.chronicle:
            hops.append(chronicle['hop'])
        if len(hops)!=len(set(hops)): 
            raise ValidationError("Chronicle hop count repeated")
        if self.isLoop():
            raise ValidationError("Chronicle UUIDs have a loop")

#     def json(self):
#         json_dict = self.chronicle
#         
#         return json_dict

 
class Task(Chronicle):
    def __init__(self, unit_id, **kwargs):
        self.unit_id = unit_id

        options = {
            'task_id' : "",
            'board' : 'Backlog',
            'command' : {},
            'response' : {},
            'chronicle' : []
            }

        options.update(kwargs)
        command_schema = config.load_schema('schema/taskschema.json')
        
        print "opyions",options
        
        try:
            validate(options, command_schema)
        except jsonschema.ValidationError:
            print "ValidationError"
            raise
        
        for key, value in options.iteritems():
            setattr(self,key, value)  
        
        if self.command == "{}":
            raise ValueError("Cannot create a new task with a blank command")
        
        #t = self.json()
        if self.task_id == "":
            # We are creating a task that does not
            # already exists on the master board, so
            # post it and get task_id number.
            self.task_id = uuid.uuid4().hex
        
            # We are creating a task that does not
            # already exists on the master board, so
            # post it and get task_id number.
            #if self.chronicle == []:
                
        self.validate_chronicle()
            
        
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
        
#     def get(self):
#         taskboard_interface.get_task(self.task_id)
#         task = taskboard_interface.get_task(self.task_id)
# 
#         return task
    def validate_response(self, task, new_task):
        mismatch = None
        for key, value in task.iteritems():
            if key <> "response":
                try:
                    if task[key] <> new_task[key]:
                        mismatch = True
                        raise ValidationError("Key " + key + " value " + str(task[key]) + " <> " + str(new_task[key]))
                except KeyError:
                    pass
                
            
        
                               
    def add_response(self, **kwargs):
      
        # kwargs is a dictionary
        # this will require some form of validation to ensure only valid keys are created.  TBD.


        # Check that the only difference is response
        self.validate_response(self.json(), kwargs)

        json_dict = {}
        for key, value in kwargs.iteritems():
            json_dict[key] = value
            setattr(self,key, value)
        
        # Do not modify task as it may be forwarded.
        # Only let taskboard do this.
        #if self.response <> {}:
        #    self.board = 'Pending'
        
        # Update chronicle with this units uuid and timer result    
        #self.chronicle_manager.update()      

        self.json()

        #taskboard_interface.patch_task(self.task_id,json_dict)
    
    def isResponse(self):
        self.listen_for_response()
        if self.response == {}:
            return False
        else:
            return True
        
    def json(self):
        # dumps ... dict to string
        # loads ... string to dict
        # Return a dict
        task_dict = {
                        "task_id" : self.task_id,
                        "title": "Blank",
                        "board": self.board, 
                        "chronicle": self.chronicle,
                        "from_unit": self.from_unit , 
                        "to_unit": self.to_unit , 
                        "command": self.command,
                        "response": self.response
                        }
        return task_dict
    
    def debug(self):
        print self.json()


