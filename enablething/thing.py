from wsgiref.simple_server import make_server
from SocketServer import ThreadingMixIn
import time
import threading

from restlite import restlite

import unit_core
import unit_custom
import config

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

def establish_network_connection():
    # Establish network connection
    pass

class UnitHandler(object):
    def __init__(self):
        self.unit_set = []
        self.tasks = []        
    
    def configure(self):
        # Instantiate new_unit depending on unit_class
        configuration = config.ThingConfiguration().load("config.json")
        thing_url = configuration["thing"]["url"]
        print "thing_url", thing_url
        thing_url =  "http://"+get_ip()
        print "thing_url", thing_url
    
    
        self.unit_set = []
        for unit_config in configuration["units"]:
            unit_id = unit_config["common"]["non_configurable"]["unit_id"]
            try:
                f = unit_config["common"]['non_configurable']['method'] 
   
                unit_module = unit_config["common"]['non_configurable']['method'].split(".")[0]
                unit_method = unit_config["common"]['non_configurable']['method'].split(".")[1]
            except IndexError:
                errornote = "Unit " +unit_id + " method " + f + " is not valid"
                raise Exception(errornote)
    
            valid_modules = {"unit_core":unit_core, "unit_custom":unit_custom}
            
            try:

                methodToCall = getattr(valid_modules[unit_module], unit_method)
                new_unit = methodToCall(thing_url, unit_config)

            except AttributeError:
                errornote = "Unit " + unit_id + " module " + unit_module + " does not have a method "+ unit_method 
                raise Exception(errornote)
            except KeyError:
                errornote = "Unit " + unit_id + " module " + unit_module + " is not unit or unit_custom"
                raise Exception(errornote)
               
            self.unit_set.append(new_unit)
    def get_thing_tasks(self, unit):
        logging.debug("get_thing_tasks() transfer unit tasks to thing list: %s tasks", len(self.tasks))
        
        n=0
        for task in self.tasks:
            if task.to_unit == unit.unit_id and task.isCommand():
                n=n+1
                unit.taskboard.add(task)
                self.tasks.remove(task)
                
            if task.from_unit == unit.unit_id and task.isResponse():
                n=n+1
                try:
                    unit.taskboard.add(task)
                    self.tasks.remove(task)
                except LookupError:
                    pass

                logging.debug("removed task %s", task.task_id)
                


    def post_thing_tasks(self, unit):
        logging.debug("post_thing_tasks() transfer thing list tasks to unit: %s tasks", len(self.tasks))
        
        # Collect things

        for task in unit.taskboard.tasks:
            for unit in self.unit_set:
                if task.to_unit == unit.unit_id:
                    # Task is for one of the hosted units
                    self.tasks.append(task)    
        
    def update(self):
        #task = None
        for unit in self.unit_set:
            
            #self.get_thing_tasks(unit)
            unit.controller_update()
            #self.post_thing_tasks(unit)
    def loop(self):
        logging.debug("loop() start")
        
        while True:
            
            self.update()

class RestHandler(object):
    def __init__(self):
        self.config = config.ThingConfiguration()
        self.config.load("config.json")
        self.port = 8080
        pass
    
    def configure(self, unit_set):
        self.routes = [(r'GET,POST /thing', self.thing)] 
        for u in unit_set:
            self.routes.append((r'GET /'+str(u.unit_id)+'/task/(?P<task_id>.*)' , u.rest.get_task))
        for u in unit_set:
            self.routes.append((r'GET /'+str(u.unit_id)+'/tasks(?P<filter_string>.*)' , u.rest.tasklistfilter))          
        for u in unit_set:
            self.routes.append((r'GET,POST /'+str(u.unit_id) , u.rest.rest_unit))
        
    @restlite.resource
    def thing():
        def GET(self, request):
            logging.debug("thing.py GET")
            
            self.config.load()     
            value = self.config.config
            return request.response((value))
        
        def POST(self, request, entity):
            logging.debug("thing.py POST")
            
            self.config.replace(entity)
            self.config.save()
            return request.response(("Thing configuration updated successfully"))
            
        return locals()

def get_ip():
    import socket

#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
#     local_ip_address = s.getsockname()[0]
#     
    local_ip_address = [(s.connect(('8.8.8.8', 80)), 
      s.getsockname()[0], 
      s.close()) for s in [socket.socket(socket.AF_INET, 
                                         socket.SOCK_DGRAM)]][0][1]
    
    return local_ip_address


def main():  
    

    
    unit_handler = UnitHandler()
    rest_handler = RestHandler()
    
    unit_handler.configure()
    rest_handler.configure(unit_handler.unit_set)
    
    httpd = make_server('', rest_handler.port, restlite.router(rest_handler.routes))


    print "Establishing unit thread"
    unitserver = threading.Thread(target=unit_handler.loop)
    unitserver.setDaemon(True)
    unitserver.start()
    
    print "Establishing server thread"
    httpserver = threading.Thread(target=httpd.serve_forever)
    httpserver.setDaemon(True)
    httpserver.start()
    
    
    


    # Ensure that each unit on this device is called
    # at the minimum update cycle



    while True:

  
        unit_handler.update()
        
        
if __name__ == "__main__": main()




