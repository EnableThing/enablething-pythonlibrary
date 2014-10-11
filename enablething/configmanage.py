import unit
import jsonschema
import json
import uuid
from jsonschema import validate

def deepMerge(d1, d2, inconflict = lambda v1,v2 : v2) :
    ''' merge d2 into d1. using inconflict function to resolve the leaf conflicts '''
    #By default it resolves conflicts in favor of values from the second dict, 
    #but you can easily override this, with some witchery 
    #you may be able to even throw exceptions out of it. :).
    for k in d2:
        if k in d1 : 
            if isinstance(d1[k], dict) and isinstance(d2[k], dict) :
                deepMerge(d1[k], d2[k], inconflict)
            elif d1[k] != d2[k] :
                d1[k] = inconflict(d1[k], d2[k])
        else :
            d1[k] = d2[k]
    return d1

def getFromDict(dataDict, mapList):
    return reduce(lambda d, k: d[k], mapList, dataDict)

def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value
    
    
def load_schema(file_name = 'schema.json'):
    with open(file_name, 'r') as f:
        configuration = json.load(f)    
    return configuration
    print configuration

def load_json(file_name = 'default_unit_config.json'):
    with open(file_name, 'r') as f:
        configuration = json.load(f)    
    return configuration



class UnitConfiguration(object):
    def __init__(self,unit_config):
        self.unit_config = unit_config
        self.schema = load_schema('../schema/thingschema.json')
        #print "self.schema", self.schema
        #print "test", {"unit":{"device_0":self.unit_config}}

        #test = {"thing": {"last_config_outcome": "","last_change_time": ""},"unit":{"device_0":self.unit_config}}

        try:
            #validate(test, self.schema)
            validate(self.unit_config, self.schema['properties']['units']['items'])
        except jsonschema.ValidationError:
            print "ValidationError"
            self.unit_config = load_json()
            self.unit_config['common']['non-configurable']['last_error'] = "Config error"
            #raise ValidationError
        #print self.unit_config
 
    def patch(self, patch):
        print "self.unit_config",self.unit_config
        patched_config = deepMerge(self.unit_config, patch)
        print "patched_config", patched_config
        
        #test = {"thing": {"last_config_outcome": "","last_change_time": ""},"unit":{"device_0":self.unit_config}}
        
        try:
            #validate(test, self.schema)
            validate(patched_config, self.schema['properties']['units']['items'])
        except jsonschema.ValidationError:
            print "ValidationError"
            raise

                    
        self.unit_config = deepMerge(self.unit_config, patch)
        self.file_write_required = True

            #raise ValidationError
        
        return self.unit_config             
        
        # validate(self.unit_config)
        
class ThingConfiguration(object):
    def __init__(self):
        self.config = None
        self.schema = load_schema('../schema/thingschema.json')
        self.units = []
        self.load()
        
        validate(self.config, self.schema)

        for unit in self.config['units']:
            self.units.append(UnitConfiguration(unit))
    
    def load(self, file_name = '../thing/config.json'):
        with open(file_name, 'r') as f:
            self.config = json.load(f)    
        #self.config = configuration
        return self.config
    
    def save(self, file_name = '../thing/config.json'):        
        with open(file_name, 'w') as outfile:
            json.dump(self.config, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

    def replace(self, configuration):
        try:
            validate(configuration, self.schema)
        except jsonschema.ValidationError:
            raise
        
        self.config = configuration
        print "self.config",self.config
        print "self.config[thing]", self.config['thing']
        return self.config  
    
    def patch(self, patch):
        self.config = deepMerge(self.config, patch)
        return self.config    
    
    def unitreport(self):
        # Return a json dictionary with information about the units
        value = []
        print "self.config", self.config
        for item in self.config['units']:
            print "item", item

            unit_id = item['common']['non_configurable']['unit_id']
            description =  item['common']['non_configurable']['description']
            function = item['common']['non_configurable']['function']
            status = item['common']['non_configurable']['status']
            
            value.append({'unit_id':unit_id, 'description':description, 'function':function, 'status':status})
            
        return value
    

                

# def configure_unit(unit_setup = unit.GenericUnit, unit_id = None, input_ids = [], update_cycle = 5, description = "Generic unit"):
#     if unit_id == None:
#         unit_id = uuid.uuid4().hex
#     # Load GUID list from configuration in GUID list
#     patch_config = {
#                         "common": {
#                             "configurable": {
#                                 "input_UUIDs": input_ids,
#                                 "update_cycle": update_cycle,
#                                 },                      
#                             "non-configurable": {
#                                 "unit_id": unit_id,
#                                 "description": description
#                                 }
#                             },
#                     }
#     
#     if unit_specific == None:
#         pass
#     else:
#         unit_config['unit_specific'] = unit_specific  
#     return unit.unit_setup(unit_config)


def main():
    c = ThingConfiguration()
    #unit_config = c.units[0].unit_config
    success_patch = {"unit_specific": {"configurable":{"this field is allowed": 9}}}

    
    unit_config = c.units[0].patch(success_patch)
    print "output", unit_config['unit_specific']["configurable"]['this field is allowed']
    

if __name__ == "__main__": main()