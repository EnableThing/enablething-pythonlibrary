#unit.py
#Unit library

import unit

import uuid
import time
import taskboard_interface
from datetime import datetime
import json

    
    

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

class MemoryUnit(unit.GenericUnit):
    def process(self):
        # No process
        pass
    def unit_startup(self):
        # TBD
        pass
    


class charOutputUnit(unit.GenericUnit):
    def display_interface(self,text):
        print "--- 16char DISPLAY ---"
        s = text[0:16] + "/n" + text[16:32]
        print s
        
        return s
        
    def process(self):
       
        if len(self.inputboard.input_container) > 1:
            raise Exception("More than one input passed to PassThruUnit.") 
        self.memory.history = self.inputboard.input_container[0].history
        self.memory.forecast = self.inputboard.input_container[0].forecast
        
        item = self.memory.latest()
        if item.time_stamp == None or item.data == None:
            return
        print "charOutputUnit", item.json()
        text = str(item.time_stamp) + str(item.data['time'])
        
        self.display_interface(text)


        #print "self.inputboard.input_container[0].history"
        #print self.inputboard.input_container[0].history
        
        #self.memory.history = 
        #self.memory.forecast = self.inputboard.input_container[0].forecast
  
  
    
    def unit_startup(self):
        #Get NTP time
        pass



def main():  
    # Instantiate a new genericunit 
    pass
        
if __name__ == "__main__": main()
