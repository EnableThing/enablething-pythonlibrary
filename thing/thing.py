#import json
from enablething import unit
from enablething import unit_custom
from enablething import taskobj
from enablething import router
from enablething import configmanage

from restlite import restlite
import json
import re

from jsonschema import validate

#import sys
from wsgiref.simple_server import make_server


function_list = {"thermometer":unit.GenericUnit,
                  "electric meter":unit.GenericUnit,
                  "noticeboard":unit.GenericUnit,
                   "clock":unit.ClockUnit,
                   "16 character display": unit_custom.charOutputUnit,
                   "passthru":unit.PassThruUnit}

#def load_schema(file_name = '../schema/schema.json'):
#    with open(file_name, 'r') as f:
#        configuration = json.load(f)    
#    return configuration
#    print configuration

command_schema = configmanage.load_schema(file_name = '../schema/commandschema.json')   
config_schema = configmanage.load_schema(file_name = '../schema/thingschema.json')

thingconfig = configmanage.ThingConfiguration()
thingconfig.load("config.json")

def configure_units():
    # Load GUID list from configuration in GUID list
    #thingconfig = configmanage.ThingConfigation()
    configuration = configmanage.ThingConfiguration().load("config.json")
    
    units = []
    for unit_config in configuration["units"]:
        unit_id = unit_config["common"]["non_configurable"]["unit_id"]
        unit_class = unit_config["common"]['non_configurable']['function']
        # Instantiate new_unit depending on unit_class
        new_unit = function_list[unit_class](unit_config)   
        units.append(new_unit)
    return units

unit_set = configure_units()


@restlite.resource
def thing():
    def GET(request):
        print "thing() GET()"
        thingconfig.load()
        # Return a JSON file with Thing status and status of all Units
        
        #unit_info = []
        #for item in thingconfig.config['units']:
        #    unit_info.append(item['common']['non_configurable'].items())
            
        #value = (('thing', thingconfig.config['thing']),('units',unit_info))        
        value = thingconfig.config
        return request.response(value)
    
    def POST(request, entity):
        configuration = entity
        #try:
        thingconfig.replace(entity)
        #except:
        #    raise restlite.Status, '400 Bad Request'
        
        thingconfig.save()
        return request.response(("Thing configuration updated successfully"))
        
        
    return locals()

def find_unit(unit_id):
    global unit_set
    for unit in unit_set:
        if unit.id == unit_id:
            return unit
    raise LookupError
    


@restlite.resource
def posttask():
    def POST(request, entity):
        print "posttask()"
        global unit_set
        unit_id = request['wsgiorg.routing_args']['unit_id']
        print "unit_id" 
        #request['PATH_INFO'][1:]
        unit = find_unit(unit_id)
        
        command = entity        
        validate(command, command_schema)
        task = taskobj.Task(unit_id, **command)
        
        try:
            unit.taskboard.find_task(task.task_id)
            unit.taskboard.respond(task.task_id, task.response)
            return request.response(("Task "+ task.task_id + "updated successfully"))
        except LookupError:
            # Means that an existing task was not found
            unit.taskboard.add(task)
            return request.response(("Task " + task.task_id + "added"))
        
        return request.response(("success"))

    return locals()

@restlite.resource
def getresponse():
    def GET(request):
        unit_id = request['wsgiorg.routing_args']['unit_id']
        task_id = request['wsgiorg.routing_args']['task_id']

        try:
            unit = find_unit(unit_id)
        except LookupError:
            raise restlite.Status, '400 Bad Request'
            return request.response(("Requested Unit UUID " + unit_id + " not present on this Thing or badly formed UUID"))     
         
        try:    
            task = unit.taskboard.find_task(task_id)
        except LookupError:
            raise restlite.Status, '400 Bad Request'
            return request.response(("Requested Task " + task_id + " not present on this Unit or badly formed Task UUID"))
        
        if task.response == {}:
            raise restlite.Status, '400 Bad Request'
            return request.response(("Requested Task" + task_id + " does not have a Response"))
        
        value = task.json().items()

        return request.response((value))     

    return locals()

@restlite.resource
def gettasklist():
    def GET(request):
        # Respond to a GET request to /unit/<unit_id>/task with the 
        # unit's current status
        
        unit_id = request['wsgiorg.routing_args']['unit_id']
        
        try:
            unit = find_unit(unit_id)
        except LookupError:
            raise restlite.Status, '400 Bad Request'
            return request.response(("Requested Unit UUID " + unit_id + "not present on this Thing or badly formed UUID"))     
        value = []
        
        for task in unit.taskboard.tasks:
            value.append(task.json().items())

        return request.response((value))     

    return locals()

@restlite.resource
def tasklistfilter():
    def GET(request):
        # Respond to a GET request to /unit/<unit_id>/task with the 
        # unit's current status
        unit_id = request['wsgiorg.routing_args']['unit_id']
        filter_string = request['wsgiorg.routing_args']['filter_string']
        
        try:
            unit = find_unit(unit_id)
        except LookupError:
            raise restlite.Status, '400 Unit not found'
        value = []
        
        if filter_string == "":
            value = []
            for task in unit.taskboard.tasks:
                value.append(task.json().items())
            return request.response((value))
            
        print "filter string", filter_string
        
        expression = "\?(?P<key>\w+)\W+(?P<value>\w+)"
        
        m = re.match(expression, filter_string)
        
        search_key = (m.group("key"))
        search_value = (m.group("value"))
        print "search_key", search_key
        print "search_value" , search_value
        filter_response = []
        for task in unit.taskboard.tasks:
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
def unitstatus():
    def GET(request):
        # Respond to a GET request to /unit/<unit_id> with the 
        # unit's current status
        
        unit_id = request['wsgiorg.routing_args']['unit_id']
         
        try:
            unit = find_unit(unit_id)
        except LookupError:
            raise restlite.Status, '400 Unit not found'
 
 
        return request.response(('status',unit.status))     
 
    return locals()

@restlite.resource
def unitreport():
    def GET(request):
        return request.response((thingconfig.unitreport()))   
    return locals()

 

# create an authenticated data model with one user and perform authentication for the resource

model = restlite.AuthModel()
model.register('nick@enablething.org', 'localhost', 'somepass')

# all the routes

routes = [
    (r'GET /unit/(?P<unit_id>.*)/task/(?P<task_id>.*)', getresponse),

    (r'GET /unit/(?P<unit_id>.*)/tasks(?P<filter_string>.*)', tasklistfilter),

    (r'GET /unit/(?P<unit_id>.*)', unitstatus),
    (r'POST /unit/(?P<unit_id>.*)', posttask),
    (r'GET /unit', unitreport),
    (r'GET,POST /thing', thing)
]     
   # (r'GET /unit/(?P<unit_id>.*)/tasks', gettasklist),
    #(r'GET /test', router.testcall)   
def establish_network_connection():
    # Establish network connection
    pass


def main():  
    global units
    port = 8080 
    
    httpd = make_server('', port, restlite.router(routes))
   
    #try: httpd.serve_forever()
    #except KeyboardInterrupt: pass
    
    # Parse configuration string to create 
    # an array containing all units.
    
    establish_network_connection()

    # Ensure that each unit on this device is called
    # at the minimum update cycle
    while True:

        # Check http
        httpd.handle_request()

        for unit in unit_set:

            unit.get_task()
        
        
if __name__ == "__main__": main()




