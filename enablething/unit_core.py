import logging

from unit import BaseUnit
from task import create_timestamp

class GenericUnit(BaseUnit):
#    def __init__(self, url, unit_config):
#        super(self.__class__, self).__init__(url, unit_config)
    
    def process (self):
        logging.info("process() %s", self.description)
        # Generic process to be overwritten by custom 
        # processes.
        # For this process just mirror inputs to output.
        #self.get_task()

        from random import randrange
        
        self.memory.add({"dummy_reading":randrange(100)})

class MemoryUnit(BaseUnit):
    def process(self):
        # No process
        pass
    def unit_startup(self):
        # TBD
        pass
    

class ClockUnit(BaseUnit):
    def process(self):
        logging.info("process() %s", self.description)
        
        #dt= datetime.now()
        #time_stamp = dt.strftime('%Y-%m-%dT%H:%M:%S')
        time_stamp = create_timestamp()
        self.memory.add({"time":time_stamp})
        
    def unit_startup(self):
        #Get NTP time
        pass

class SimpleForecastUnit(BaseUnit):
    def process(self):
        print "PassThruUnit process()"
        # For the PassThruUnit take the latest received memory and make the units
        # memory reflect this.
        # Raise an exception if there is more than one input
        
        # Get the next completed input set
        logging.info("start process() %s", self.description)
        
        ''' Take last value and forecast this out for an hour '''

        logging.debug("Passing input to memory")

        if len(self.inputboard.input_container) > 1:
            raise Exception("More than one input passed to ForecastUnit.")
        
        self.memory.history = self.inputboard.input_container[0].history
        self.memory.forecast = self.inputboard.input_container[0].forecast


        # See if there is any data to extrapolate 
        try:
            data = self.memory.history[0].data
            start_time = taskobj.load_timestamp(self.memory.history[0].time_stamp)
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
            time_stamp = taskobj.create_timestamp(ts)
            self.memory.add_forecast(data, time_stamp)        
  
    def unit_startup(self):
        pass

class PassThruUnit(BaseUnit):
    def process(self):
        print "PassThruUnit process()"
        # For the PassThruUnit take the latest received memory and make the units
        # memory reflect this.
        # Raise an exception if there is more than one input
        
        # Get the next completed input set
        logging.info("start process() %s", self.description)
        
        
        if len(self.inputboard.input_container) > 1:
            raise Exception("More than one input passed to PassThruUnit.")

        logging.debug("Passing input to memory")
        print "self.inputboard.input_container[0].history"
        print self.inputboard.input_container[0].history
        
        self.memory.history = self.inputboard.input_container[0].history
        self.memory.forecast = self.inputboard.input_container[0].forecast
  

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
