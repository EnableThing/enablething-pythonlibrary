import re
import json
import random
import time
import uuid
from datetime import datetime

import requests
from restlite import restlite

from task import Task

class RestClient(object):
    def __init__(self, url, unit_id):
        # url : "http://<ip address>:<port>"
        # unit_id = "aadf..."
        
        self.url = url
        self.unit_id = unit_id
        self.response = None
    
    def get_responses(self, url = "", unit_id = ""):
        
        #u = unit_id.replace("-", "")
        request_url = url + "/unit/" + self.unit_id + "/tasks?board=In progress"
        print "url",url
        
        #getURL = "http://127.0.0.1:8000/api/tasks/to_unit/"+ u + "/?board=Backlog"
       
        response = requests.get(url = request_url,
                         data={},
                         headers={"Accept": "application/json"},
                         cookies=None,
                         auth=None)
        response.raise_for_status()
    
        return json.loads(response.content)
    
class RestServer(object):
    def __init__(self, unit_id, taskboard, router):
        self.unit_id = unit_id
        self.taskboard = taskboard
        self.router = router
    

    
            
    @restlite.resource
    def get_task():
        def GET(self, request):
            task_id = request['wsgiorg.routing_args']['task_id']
            self.taskboard.debug()
          
            try:    
                task = self.taskboard.find_task(task_id)
            except LookupError:
                raise restlite.Status, '400 Bad Request'
                return request.response(("Requested Task " + task_id + " not present on this Unit or badly formed Task UUID"))
            
            if task.response == {}:
                raise restlite.Status, '404 Not Found'
                return request.response(("Requested Task" + task_id + " does not have a Response"))
            
            value = task.json().items()

            return request.response((value))  
        return locals()
    
    @restlite.resource
    def tasklistfilter():
        def GET(self, request):
            # Respond to a GET request to /unit/<unit_id>/task with the 
            # unit's current status
            filter_string = request['wsgiorg.routing_args']['filter_string']
            
            value = []  
            if filter_string == "":
                value = []
                for task in self.taskboard.tasks:
                    value.append(task.json().items())
                return request.response((value))
                
            expression = "\?(?P<key>\w+)\W+(?P<value>\w+)"       
            m = re.match(expression, filter_string)
            search_key = (m.group("key"))
            search_value = (m.group("value"))
            
            filter_response = []
            for task in self.taskboard.tasks:
                for key, value in task.json().iteritems():
                    print "k,v", key, value
                    if search_key == key and search_value == value: 
                        filter_response.append(task.json().items())
            
            if filter_response == []:
                raise restlite.Status, '400 Bad Request'
                return request.response(("Filter strong not found"))     
    
            return request.response((filter_response))     

        return locals()
    
    @restlite.resource
    def rest_unit():

        def GET(self, request):
            print "restunit() GET"
            # Respond to a GET request to /unit/<unit_id>/task with the 
            # unit's current status   
            value = []
            for task in self.taskboard.tasks:
                value.append(task.json().items())
            return request.response((self.unit_id,value))     
        
        def POST(self, request, entity):
            command = json.loads(entity)  
            
                
            #try:
            task = Task(self.unit_id, **command)
            #except:
            #    raise
            self.router.process_task(task)

        return locals()   