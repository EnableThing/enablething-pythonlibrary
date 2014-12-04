#unit.py
#Unit library

import unit

from unitcontroller import BaseUnit
import uuid
import time
import requests, json
#import taskboard_interface
from datetime import datetime
import json
import logging 
    

#class TypicalInputUnit(GenericUnit):
#    def process (self):
#        # self.get_task()
#      # self.update_memory(### observation/sensor data ####)
#    def unit_startup (self):
#        # Specific start-up requirements

#class TypicaProcessUnit(GenericUnit):     
#    def process (self):
#        # self.getask()
#        # if not self.taskboard.isResponse(self.set_id):
#        #     return
#      # Perform some function on 
#        # self.taskboard.response(task_id, response)
#    def unit_startup (self):
#        # Specific start-up requirements

#class TypicaOutputUnit(GenericUnit):     
#    def process (self):
#        # self.get_task()
#        # if not self.taskboard.isResponse(self.set_id):
#        #     return
#      # Perform some function on 
#        # self.taskboard.response(task_id, response)
#    def unit_startup (self):
#        # Specific start-up requirements

class MemoryUnit(BaseUnit):
    def process(self):
        # No process
        pass
    def unit_startup(self):
        # TBD
        pass
    


class charOutputUnit(BaseUnit):
    def display_interface(self,text):
        print "--- 16char DISPLAY ---"
        s = text[0:16] + "/n" + text[16:32]
        print s
        
        return s
        
    def process(self):
       
        if len(self.inputconnector.inputunits) > 1:
            raise Exception("More than one input passed to PassThruUnit.") 
        
        datapoint = self.inputconnector.inputunits[0].memory.current_datapoint().json()
        if datapoint['data'] != None:     
            self.memory.add(data = datapoint['data'], time_stamp = datapoint['time_stamp'])

        
        item = self.memory.current_datapoint()
        if item.time_stamp == None or item.data == None:
            return
        print "charOutputUnit", item.json()
        print "item.data",item.data
        text = str(item.time_stamp) + str(item.data)
        
        self.display_interface(text)


        #print "self.inputboard.input_container[0].history"
        #print self.inputboard.input_container[0].history
        
        #self.memory.history = 
        #self.memory.forecast = self.inputboard.input_container[0].forecast
  
class weatherInputUnit(BaseUnit):
    def display_interface(self,text):
        print "--- 16char DISPLAY ---"
        s = text[0:16] + "/n" + text[16:32]
        print s
        
        return s
        
    def process(self):
        logging.debug("process() %s", self.description)
        
        #dt= datetime.now()
        #time_stamp = dt.strftime('%Y-%m-%dT%H:%M:%S')
        #
        
        url = self.url
        KEY = self.key
        FEATURE=self.feature
        FORMAT="json"
        QUERY=self.query
        

        
        getURL = url+KEY+"/"+FEATURE+"/q/"+QUERY+"."+FORMAT
        print "getURL",getURL
        r = requests.get(getURL,
                         data={},
                         headers={},
                         cookies=None,
                         auth=None)
        r.raise_for_status()
        
        content = json.loads(r.content)
        print "content", r.content
        print "content", content
        observation_time_rfc822 = content['current_observation']['observation_time_rfc822']
        temp_c = content['current_observation']['temp_c']
        
        self.memory.add({"temp_c":temp_c}, time_stamp = observation_time_rfc822)       
    
    def unit_startup(self):
        #Get NTP time
        pass



def main():  
    # Instantiate a new genericunit 
    pass
        
if __name__ == "__main__": main()
