
import time, datetime
from email import utils
from jsonschema import validate

import taskboard_interface
import configmanage

import logging

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
        self.schema = configmanage.load_schema('../schema/memoryschema.json')  


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
    def __init__(self, unit_id, chronicle):
        self.unit_id = unit_id
        self.start_time = time.time()
        if chronicle == None or chronicle == []:
            self.hops = 0
            self.chronicle = []
            self.update()
        else:
            self.hops = len(chronicle)
            self.chronicle = chronicle
        
        self.visited_uuids = []
# 
#         for item in self.chronicle:
#             self.visited_uuids.append(item["unit_id"])

    def last(self):
        return self.chronicle[-1]["unit_id"]
        
    def next(self, current_unit_id):
        index = next(index for (index, d) in enumerate(self.chronicle) if d["unit_id"] == current_unit_id)
        if index + 1 > len(self.chronicle):
            raise LookupError("Lookup uuid is last in list")
        # Return the next unit visited after 'current_unit_id'
        
        return self.chronicle[index + 1]["unit_id"]
    
    def previous(self, current_unit_id):
        # Return the previous unit visited before 'current_unit_id'
        # This allows the path back to the originating unit to be traced.
        index = next(index for (index, d) in enumerate(self.chronicle) if d["unit_id"] == current_unit_id)
        
        if index == 0:
            raise LookupError("Lookup UUID is first in list")
        return self.chronicle[index - 1]["unit_id"]
                
    def update(self):
        elapsed_time = time.time() - self.start_time
        self.chronicle.append({"hop":self.hops + 1, "unit_id": self.unit_id, "time_ms": 1000*round(elapsed_time,3)})
        #self.task.update(chronicle = updated_chronicle)    

    def json(self):
        json_dict = self.chronicle
        
        return json_dict

       
    
class Task(object):
    def __init__(self, unit_id, **kwargs):
        #self.start_time = time.time()

        options = {
            'task_id' : "",
            'board' : 'Backlog',
            'command' : {},
            'response' : {},
            'chronicle' : []
            }

        options.update(kwargs)
        
              
        for key, value in options.iteritems():
            setattr(self,key, value)  

                  
        self.chronicle_manager = Chronicle(unit_id, self.chronicle)
        
        if self.command == "{}":
            raise Exception("Cannot create a new task with a blank command")
        
        #t = self.json()
        if self.task_id == "":
            # We are creating a task that does not
            # already exists on the master board, so
            # post it and get task_id number.
            if self.chronicle == []:
                self.chronicle_manager.update()
            t = self.json()
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
        
        # Update chronicle with this units uuid and timer result    
        self.chronicle_manager.update()      

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
                        "chronicle": self.chronicle_manager.json(),
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

