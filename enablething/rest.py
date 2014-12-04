import re
import json
import random
import time
import uuid
from datetime import datetime
import logging

import requests
from requests import HTTPError
from restlite import restlite

from jsonschema import ValidationError

from task import Task
from enablethingexceptions import TaskError, TaskboardError

class RequestCache(object):
    def __init__(self, max_cache_age):
        self.cache = {}
        self.max_cache_age = max_cache_age
    
    def get(self, request):
        for key, value in self.cache.items():
            if key == request:
                return value['response']
        return None
    
    def add(self, request, response):
        self.cache[request] = {"time_stamp":time.time(),
                               "response":response}
        self.remove_old()
    def remove_old(self):
        for key, value in self.cache.items():
            if value['time_stamp'] - time.time() > self.max_cache_age:
                del self.cache[key]
        
        
        

class RequestHandler(object):
    def __init__(self, ip, port, unit_id):
        # url : "http://<ip address>:<port>"
        # unit_id = "aadf..."
        
        self.url = "http://" + str(ip) + ":" + str(port)
        
        self.unit_id = unit_id
        self.response = None
        self.cache_handler = RequestCache(0)
        
    def post(self, url, json_dict):
        logging.info("post()") 
        assert type(json_dict) is dict, "json input is not dictionary: %r" % id

        request_url = self.url + "/" + url

        logging.info("post() url  %s", request_url)  
        logging.info("post() json %s", json_dict)        
       
        response = requests.post(url = request_url,
                         json = json.dumps(json_dict),
                         headers = {'Content-Type': 'application/json'},
                         cookies=None,
                         auth=None)

#                          timeout=0.5)

        response.raise_for_status()
        logging.debug("rest.post successful")

        if json_dict['response'] <> {}:
            logging.info("RESPONSE SENT via POST")
        else:
            logging.info( "COMMAND SENT via POST")
        return response.content
    
    def get(self, url):

        request_url = self.url + "/" + url
        
        response = self.cache_handler.get(request_url)
        if response != None:
            return response
        
        logging.debug("get() %s", request_url)  
       
        response = requests.get(url = request_url,
                         data={},
                         headers={"Accept": "application/json"},
                         cookies=None,
                         auth=None)
        try:
            response.raise_for_status()
        except HTTPError as e:
            print e.message
            logging.error("HTTP Error %s", e.message)
            return {}
            
        logging.debug("post() %s", response.content)  
    
        self.cache_handler.add(request_url, json.loads(response.content))
    
        return json.loads(response.content)
    
    
    
    
class RestServer(object):
    def __init__(self, unit_id, taskboard, router):
        
        self.unit_id = unit_id
        self.taskboard = taskboard
        self.router = router
        # Use this variable to identify neighbours who are able to post
        # directly to this unit.
        self.neighbours_post_enabled = []
     
    @restlite.resource
    def get_task():
        def GET(self, request):
            logging.info("get_task()")
            # GET request passed to unit
            task_id = request['wsgiorg.routing_args']['task_id']
            self.taskboard.debug()
          
            try:    
                task = self.taskboard.find_task(task_id)
            except LookupError:
                request.response(("Requested Task " + task_id + " not present on this Unit or badly formed Task UUID"))
                raise restlite.Status, '400 Bad Request'
                #return request.response(("Requested Task " + task_id + " not present on this Unit or badly formed Task UUID"))
            
            if task.response == {}:
                request.response(("Requested Task" + task_id + " does not have a Response"))
                raise restlite.Status, '404 Not Found'
                #return request.response(("Requested Task" + task_id + " does not have a Response"))
            
            #value = task.json().items()
            value = task.json()

            return request.response(value)  
        return locals()
    
    @restlite.resource
    def tasklistfilter():
        def GET(self, request):
            logging.info("tasklistfilter() GET")
            # Respond to a GET request to /<unit_id>/tasks<filter_string>
            
            filter_string = request['wsgiorg.routing_args']['filter_string']
            logging.debug("get() %s", filter_string)  
            
            
            value = []  
            if filter_string == "":
                logging.debug("get() all tasks")
                
                #value = []
#                 for task in self.taskboard.tasks:
#                     value.append(task.json().items())
#                 return request.response((value))
                filter_response = {}
                for i, task in enumerate(self.taskboard.tasks):
                    filter_response["task_"+str(i)]=task.json()
                return request.response((filter_response))
            if filter_string == "?command":
                logging.debug("get() only commands")
                
                filter_response = {}
                for i, task in enumerate(self.taskboard.tasks):
                    if task.response == {}:
                        filter_response["task_"+str(i)]=task.json()
                return request.response((filter_response))

            if filter_string == "?response":
                logging.debug("get() only responses")
                filter_response = {}
                for i, task in enumerate(self.taskboard.tasks):
                    if task.response <> {} and task.board <> "Complete":
                        filter_response["task_"+str(i)]=task.json()
                return request.response((filter_response))

                
            expression = "\?(?P<key>\w+)\W+(?P<value>\w+)"       
            m = re.match(expression, filter_string)
            search_key = (m.group("key"))
            search_value = (m.group("value"))
            
            filter_response = {}
            for i, task in enumerate(self.taskboard.tasks):

                for key, value in task.json().iteritems():

                    if search_key == key and search_value == value: 
                        #filter_response.append(task.json().items())
                        filter_response[str(i)]=task.json()
            
            if filter_response == {}:
                raise restlite.Status, '400 Bad Request'
                return request.response(("Filter strong not found"))     

            return request.response((filter_response))     

        return locals()
    
    @restlite.resource
    def rest_unit():

        def GET(self, request):
            logging.info("restunit() GET")
            
            # Respond to a GET request to /unit/<unit_id>/task with the 
            # unit's current status   
            
            tasklist = []
            for task in self.taskboard.tasks:
                tasklist.append((task.task_id, task.isResponse()))
            
            rests = []    
            for neighbour in self.router.neighbours:
                rests.append((neighbour.unit_id, ("gets",neighbour.gets),("posts",neighbour.posts)))
                
                
            return request.response(("Status", ("Tasks",tasklist),("Rest",rests)))    
        
        def POST(self, request, entity):
            logging.info("restunit() POST")
            command = json.loads(entity)
            #command = json.loads(entity)
            assert(type(command)==dict)  
              
                  
            try:
                task = Task(self.unit_id, **command)
            except TaskError:
                logging.error("POST request received with nonvalid task.")
                return request.response(("Invalid response"))
            
            try:
                neighbour_id = task.previous_neighbour
                self.router.subscriptions.unsubscribe_neighbour(neighbour_id)
                self.router.subscriptions.post_capable(neighbour_id)
            except IndexError:
                pass
            except HTTPError as e:
                logging.error("HTTPError raised %s", e.message)
            
            logging.debug("task.add_chronicle()")
            
            logging.debug("Added task %s to RX queue", task.task_id[:4])
            self.router.received.queue(task)

        return locals()   