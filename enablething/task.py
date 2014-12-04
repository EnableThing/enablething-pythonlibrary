
import time
import copy
import datetime
from email import utils
import uuid
import logging

from jsonschema import validate, ValidationError
import jsonschema


import config
from enablethingexceptions import TaskError

def shortid(id):
    if id == None:
        return "----"
    else:
        return id[:4] + "..."

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
        #print "type(data)",type(data)
        assert(isinstance(data, dict))
        logging.debug("Memory add()")
        self.history.insert(0, DataPoint(data, time_stamp))

    def remove(self, datapoint):
        raise NotImplemented
        self.history.remove(datapoint)

    def validate(self, json_dict):
        return validate(json_dict, self.schema)
        
    # This might not be required     
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
    
    def current_datapoint(self):
        try:
            return self.history[0]
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
        logging.debug("Memory debug /n %s", self.json())
        



class Chronicle(object):
    # Class to extract and write chronicle to message
    def __init__(self, to_unit):
        self.chronicle_start_time = time.time()
        self.closed = False
        self.to_unit = to_unit
#        print "a", self.chronicle

        self.load()
        self.update()
        
        self.chronicle.append({"hop":self.current_hop, "unit_id": self.unit_id, "time_ms": None})

        #print "b", self.chronicle     
        self.visited_units = [None] * len(self.chronicle)
        self.costs = [None] * len(self.chronicle)
        for chronicle in self.chronicle:

            index = chronicle['hop']

            
            self.visited_units[index] = chronicle['unit_id']
            self.costs[index] = chronicle['time_ms']

            if chronicle['hop'] > self.current_hop:

                self.current_hop = chronicle['hop']
        
        self.update()

        
             
    def update(self):

        self.cleave_chronicle()
        try:
            self.previous_neighbour =  self.visited_units[-2]
        except IndexError:
            self.previous_neighbour = None
        
        self.next_neighbour = self.get_next_neighbour()

        
    def load(self):
        self.current_hop = -1

        self.visited_units = [None] * len(self.chronicle)
        self.costs = [None] * len(self.chronicle)
        for chronicle in self.chronicle:

            index = chronicle['hop']

            
            self.visited_units[index] = chronicle['unit_id']
            self.costs[index] = chronicle['time_ms']

            if chronicle['hop'] > self.current_hop:

                self.current_hop = chronicle['hop']
                
        self.current_hop = self.current_hop + 1                   

    def get_next_neighbour(self):
        if len(self.bant) == 0:
            return None
            
        index = len(self.fant) - len(self.bant)
        if index == 0:
            return None
        else:
            return self.fant[index - 1]
            
            

    def cleave_chronicle(self):
        logging.info("cleave_chronice()")
        # Split the chronicle into FANT and BANT
        fant = True
        
        self.fant = []
        self.bant = []
        for unit in self.visited_units:
            if fant:
                self.fant.append(unit)
            
            if unit == self.to_unit:
                fant = False
            
            if not fant:
                self.bant.append(unit)
        

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
        return self._longestrun(self.fant)
    
    def current_unit(self):
        return self.visited_units[-1]  
    
    def get_unit_from_hop(self, hop):
        return self.visited_units[hop - 1]


    def get_hop_cost(self, hop):
        return self.costs[hop - 1]
        #raise LookupError("Hop not found in chronicle")
       
    def response_time_stamp(self):
        for index, unit_id in enumerate(self.visited_units):
            if unit_id == self.to_unit:
                # This is the unit the task was sent to
                return self.costs[index]
        raise LookupError
        
    def close_chronicle(self):
        if self.isClosed():
            logging.error("Task" + self.task_id[:4] + "is already closed" + self.chronicle_debug())
            #raise TaskError("Chronicle is already closed")
        
        logging.info("Task %s Previous neighbour %s, unit %s", shortid(self.task_id), shortid(self.previous_neighbour), shortid(self.unit_id))
            
        elapsed_time = time.time() - self.chronicle_start_time     
   
        self.chronicle[-1]["time_ms"] = 1000*round(elapsed_time,3) 
        self.validate_chronicle()


    def isClosed(self):
        return self.chronicle[-1]["time_ms"] != None
            
        

    def cost(self):
        # Calculate "cost" of the chronicle record
        sum_cost = 0

        for cost in self.costs:
            if cost == None:
                c = 0
            else:
                c = cost
            sum_cost += c

        return sum_cost
    
    def cost_to_unit(self, unit_id):
        # a: 10
        # b: 10
        # c: 10
        # d: 10
        # c: 10
        # b: 10
        
        # cost for unit_id is the cost of going from self.unit_id to specific unit_id (ignore cost of return trip)
        # fant = [a,b,c,d]
        # bant = [d,c,b]

        isSum = False
        sum = 0
        for index, unit in enumerate(self.fant):
            if unit == unit_id:
                isSum = True
            if isSum:

                if self.costs[index] == None:
                    x = 0
                else:
                    x = self.costs[index]
                sum = sum + x
        if isSum == False:
            raise TaskError("unit not found")

        return sum
                  

    def remove_loop(self):
        # [a,b,c,d,e,d,c] okay
        # [a,b,c,d,c,d] not okay
        # [a,b,c,d,d] not okay
        # [a,b,c,d,c,f] not okay
        # [a,b,c,d,c,b,c] not okay
        
        #print "myList", units
        myList = list(self.visited_units)
        
        repeated_patterns = []
        longest_list = []
        
        for n in xrange(2, len(myList)):
            pattern = myList[-n:]
           #if len(self._subfinder(myList, pattern)) > 1:
            #    repeated_patterns.append(self._subfinder(myList, pattern))
            #if len(self._subfinder(myList, pattern)) > len(longest_list):
            longest_list = self._subfinder(myList, pattern)[0]
        #print "longest_list",longest_list
        
        logging.info("%s",self.chronicle)
        i = 0
        for counter in xrange(len(longest_list)):
            i = i + 1
            self.chronicle.pop()
            #logging.info("IndexError: pop from empty list %s %s %s %s", counter, len(longest_list), len(self.chronicle), i)
            
#     def neighbour_destination_cost(self):
#         cost = 0
#         # [a,b,c,b]
#         # 2 out of 3 3/2+1
#         # No match for a => return cost of (b,c)
#         # [a,b,c]
#         # No match => return zero cost ... means we are at c
#         # [a,b,a]
#         # 1 out of 2 3/2 +1
#         # Means we are at a => retrun cost of (a,b)
#         # [a,b,c,b]
#         # 2 out of 3 = 3/2 + 1        
#         # [a,b,c,d,e,d,c]
#         # 3 out of 6 = 6/2
# 
#         repeated_uuid = []
#         seen_uuid = []
#         start_calc = False
#         cost = None
#         # Find non-repeated uuid positions
#         for index, unit_id in enumerate(self.fant):
#             if unit_id == self.unit_id:
#                 start_calc = True
#             if start_calc:
#                 if cost == None:
#                     cost = 0
#                 cost = cost + self.costs[enumerate]
# 
#         return cost
        
        
    
    def validate_chronicle(self):
        logging.info("validate_chronicle() of task %s", self.task_id[:4])
        # Check for non-unique hop count
        hops = []
#         last_unit_id = None
        for chronicle in self.chronicle:
            hops.append(chronicle['hop'])
             #last_unit_id = chronicle['unit_id']
        
        if self.isClosed() == False:
            if self.previous_neighbour == self.unit_id and self.current_hop > 1:
                raise ValidationError("Chronicle last hop "+shortid(self.previous_neighbour) + " was this unit")
                  
        if len(hops)!=len(set(hops)): 
            logging.error(self.chronicle)
            raise ValidationError("Chronicle hop count repeated")
        if self.isLoop():
            raise ValidationError("Chronicle UUIDs have a loop")
        
        old_chronicle_id = None
        for chronicle in self.chronicle:
            if chronicle['unit_id'] == old_chronicle_id:   
                self.debug()              
                logging.error("Hop repeated in task %s chronicle %s", self.task_id[:4], self.chronicle_debug())
                raise ValidationError("Hop repeated in succession")
            old_chronicle_id = chronicle['unit_id']
        
        
    def chronicle_debug(self):
        #chronicle_string =  "                     "
        chronicle_string = ""
        for counter, chronicle in enumerate(self.chronicle):
            chronicle_string = chronicle_string + chronicle['unit_id'][:4]
            if counter < len(self.chronicle):
                chronicle_string = chronicle_string + ">"

        return chronicle_string


 
class Task(Chronicle):
    def __init__(self, unit_id, **kwargs):
        self.processed_time = 0
        self.index = 0
        self.send_retries = 0
        self.unit_id = unit_id
        self.note = ""
        self.status = "Created"
        #self.isRouted = False
        self.processed = False
        options = {
            'task_id' : "",
            'board' : 'Backlog',
            'command' : {},
            'response' : {},
            'chronicle' : []
            }

        options.update(kwargs)
        command_schema = config.load_schema('schema/taskschema.json')


        
        try:
            validate(options, command_schema)
        except jsonschema.ValidationError:            
            raise TaskError("Validation error - can't create task")
        
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

        assert(self.to_unit != None)
        Chronicle.__init__(self,self.to_unit)        
        
        
        try:        
            self.validate_chronicle()
        except ValidationError:
            raise TaskError
        
        logging.info("Unit %s Task %s chronicle path %s", self.unit_id[:4], self.task_id[:4], self.chronicle_debug())

            
        self.send_retries = 0
        
        self.json()
        
        logging.debug("Task: New task created")

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
        
        self.json()
    
    def isResponse(self):
        return self.response <> {} and self.command <> {}
            
        
    def isCommand(self):
        return self.command <> {} and self.response == {}
            
        
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

        #print "task %s ttl %s from %s to %s command %s isResponse %s" % (self.task_id[:4], self.cost(), self.from_unit[:4], self.to_unit[:4], self.command.keys()[0],self.isResponse())
        print "%2.0f %1s %4s %4s %2.0f %6.0fms %4s %1s %10s %5s %25s %40s" % (self.index, ("-","P")[self.processed], self.unit_id[:4], self.task_id[:4], self.send_retries, self.cost(), self.from_unit[:4], self.to_unit[:4], self.command.keys()[0],("-","R")[self.isResponse()], self.note, self.chronicle_debug())

