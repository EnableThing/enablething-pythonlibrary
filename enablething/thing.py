from wsgiref.simple_server import make_server

from restlite import restlite

import unit
import unit_custom
import config

def establish_network_connection():
    # Establish network connection
    pass

class UnitHandler(object):
    def __init__(self):
        self.unit_set = []        
    
    def configure(self):
        # Instantiate new_unit depending on unit_class
        configuration = config.ThingConfiguration().load("config.json")
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
    
            valid_modules = {"unit":unit, "unit_custom":unit_custom}
            
            try:
                methodToCall = getattr(valid_modules[unit_module], unit_method)
                new_unit = methodToCall(unit_config)
            except AttributeError:
                errornote = "Unit " + unit_id + " module " + unit_module + " does not have a method "+ unit_method
                raise Exception(errornote)
            except KeyError:
                errornote = "Unit " + unit_id + " module " + unit_module + " is not unit or unit_custom"
                raise Exception(errornote)
               
            self.unit_set.append(new_unit)
        
    def request_update(self):
        for unit in self.unit_set:
            unit.get_task()

class RestHandler(object):
    def __init__(self):
        self.config = config.ThingConfiguration()
        self.config.load("config.json")
        self.port = 8080
        pass
    
    def configure(self, unit_set):
        self.routes = [(r'GET,POST /thing', self.thing)] 
        for u in unit_set:
            self.routes.append((r'GET /unit/'+str(u.unit_id)+'/task/(?P<task_id>.*)' , u.rest.get_task))
        for u in unit_set:
            self.routes.append((r'GET /unit/'+str(u.unit_id)+'/tasks/(?P<filter_string>.*)' , u.rest.tasklistfilter))          
        for u in unit_set:
            self.routes.append((r'GET,POST /unit/'+str(u.unit_id) , u.rest.rest_unit))
        
    @restlite.resource
    def thing():
        def GET(self, request):
            print "thing() GET()"
            self.config.load()     
            value = self.config.config
            return request.response(value)
        
        def POST(self, request, entity):
            self.config.replace(entity)
            self.config.save()
            return request.response(("Thing configuration updated successfully"))
            
            
        return locals()


def main():  
    unit_handler = UnitHandler()
    rest_handler = RestHandler()
    unit_handler.configure()
    rest_handler.configure(unit_handler.unit_set)
    
    httpd = make_server('', rest_handler.port, restlite.router(rest_handler.routes))
    
    establish_network_connection()

    # Ensure that each unit on this device is called
    # at the minimum update cycle
    while True:

        httpd.handle_request()
        unit_handler.request_update()
        
        
        
if __name__ == "__main__": main()




