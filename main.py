#Outline code


import json
import unit

##class CustomUnit(GenericUnit):
##    def process (self):
##    # Typical unit
##        self.get_inputs()
##
##
##        # Perform device function ie 
##        # . take an observation, 
##        # . process, or 
##        # . change setting
##
##
##        #Update units Memory
##        self.request ("memory", {memory_GUID, Memory})
##        self.status = "ready"
##
##
##    def ondevice_display(self):
##        # Update LCD, LEDs, console, etc
##        pass
##
##    def unit_startup (self):
##        # TBD
##        pass


def load_persistent_configuration():
    # Load persistent configuration


    #If "Attempt failed": 
    #Last persistent memory reload failed for some reason.  load in #default configuration - which can be in the code")


    #with open('config.json', 'w') as f:
    #json.dump(configuration, f)


#   else
#       Write "Attempt failed" to a place in persistent memory.
#       try:
    with open('config.json', 'r') as f:
        configuration = json.load(f)
#       except:
#           Write "Attempt successful"
    
    return configuration


def establish_network_connection():
    # Establish network connection
    pass

function_list = {"thermometer":unit.GenericUnit,
                  "electric meter":unit.GenericUnit,
                   "clock":unit.ClockUnit,
                   "16 character display": unit.charOutputUnit,
                   "passthru":unit.PassThruUnit}

def configure_units():
    # Load GUID list from configuration in GUID list
    configuration = load_persistent_configuration()

    units = []
    for unit_config in configuration["unit"].values():

        unit_id = unit_config["common"]["non-configurable"]["unit_id"]
        print unit_id
        unit_class = unit_config["common"]['non-configurable']['function']
        print unit_class

        # Instantiate new_unit depending on unit_class
        new_unit = function_list[unit_class](unit_config)
    
        units.append(new_unit)

    return units


def main():  
    # Parse configuration string to create 
    # an array containing all units.
    units = configure_units()
    establish_network_connection()

    # Ensure that each unit on this device is called
    # at the minimum update cycle
    while True:
        for unit in units:

            unit.process()
        
        
if __name__ == "__main__": main()



