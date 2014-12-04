import logging
import datetime

from unitcontroller import BaseUnit
from task import Task, create_timestamp, load_timestamp

class PassThruUnit(BaseUnit):
    def process(self):
        
        # For the PassThruUnit take the latest received memory and make the units
        # memory reflect this.
        # Raise an exception if there is more than one input
        
        # Get the next completed input set
        logging.debug("PassThruUnit process() %s", self.description)
        
        
        if len(self.inputconnector.inputunits) > 1:
            raise Exception("More than one input passed to PassThruUnit.")
        if len(self.inputconnector.inputunits) == 0:
            logging.info("No input passed to PassThruUnit.")
            raise Exception("No input passed to PassThruUnit.")
            return

        logging.debug("Passing input to memory")
        logging.debug("self.inputconnector.inputunits[0].memory.history %s", self.inputconnector.inputunits[0].memory.history)
        
        datapoint = self.inputconnector.inputunits[0].memory.current_datapoint().json()
        print "datapoint", datapoint
        if datapoint['data'] != None:
            print "adding datapoint to memory"
            print "datapoint", datapoint     
            self.memory.add(data = datapoint['data'], time_stamp = datapoint['time_stamp'])

        
  

    def unit_startup(self):
        pass

class GenericUnit(BaseUnit):
#    def __init__(self, url, unit_config):
#        super(self.__class__, self).__init__(url, unit_config)
    
    def process (self):
        logging.debug("GenericUnit process() %s", self.description)
        # Generic process to be overwritten by custom 
        # processes.
        # For this process just mirror inputs to output.
        #self.get_task()

        from random import randrange
        
        self.memory.add({"dummy_reading":randrange(100)})

class RandomUnit(BaseUnit):
#    def __init__(self, url, unit_config):
#        super(self.__class__, self).__init__(url, unit_config)
    
    def process (self):
        logging.debug("RandomUnit process() %s", self.description)
        # Generic process to be overwritten by custom 
        # processes.
        # For this process just mirror inputs to output.
        #self.get_task()

        from random import randrange
        
        self.memory.add({"random_number":randrange(100)})

class MemoryUnit(BaseUnit):
    def process(self):
        # No process
        pass
    def unit_startup(self):
        # TBD
        pass
    

class ClockUnit(BaseUnit):
    def process(self):
        logging.debug("ClockUnit process() %s", self.description)
        
        #dt= datetime.now()
        #time_stamp = dt.strftime('%Y-%m-%dT%H:%M:%S')
        time_stamp = create_timestamp()
        self.memory.add({"time":time_stamp})
        
    def unit_startup(self):
        #Get NTP time
        pass

class SimpleForecastUnit(BaseUnit):
    def process(self):
        logging.debug("SimpleForecastUnit process()")
        
        # For the PassThruUnit take the latest received memory and make the units
        # memory reflect this.
        # Raise an exception if there is more than one input
        
        # Get the next completed input set
        logging.debug("start process() %s", self.description)
        
        ''' Take last value and forecast this out for an hour '''

        logging.debug("Passing input to memory")

        if len(self.inputconnector.inputunits) > 1:
            raise Exception("More than one input passed to ForecastUnit.")
        
        self.memory.history = self.inputconnector.inputunits[0].memory.history
        self.memory.forecast = self.inputconnector.inputunits[0].memory.forecast


        # See if there is any data to extrapolate 
        try:
            data = self.memory.history[0].data
            start_time = load_timestamp(self.memory.history[0].time_stamp)
        except IndexError:
            data = None
            start_time = datetime.datetime.now()

        if self.update_cycle <= 0:
            delta_t = 60*5    
        else:
            delta_t = self.update_cycle
        print "data", data
        
        self.memory.forecast = []
        for i in xrange(10):
            ts = start_time + datetime.timedelta(seconds = i * delta_t)            
            time_stamp = create_timestamp(ts)
            self.memory.add_forecast(data, time_stamp)        
  
    def unit_startup(self):
        pass



class NullUnit(BaseUnit):
    def process(self):
        print "NullUnit process()"
        raise NotImplemented
    def unit_startup(self):
        pass

class AND(BaseUnit):
    def process(self):
        #self.requestinputs()
        
        pass
    def unit_startup(self):
        #Get NTP time
        pass

class OR(BaseUnit):
    pass

class NOT(BaseUnit):
    pass

class XOR(BaseUnit):
    pass

def main():  
    pass
        
if __name__ == "__main__": main()
