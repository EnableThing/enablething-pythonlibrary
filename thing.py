#Outline code


import json
import unit
import unit_custom


def load_persistent_configuration(file_name = 'configmanage.json'):
    # Load persistent configuration


    #If "Attempt failed": 
    #Last persistent memory reload failed for some reason.  load in #default configuration - which can be in the code")


    #with open('configmanage.json', 'w') as f:
    #json.dump(configuration, f)


#   else
#       Write "Attempt failed" to a place in persistent memory.
#       try:
    with open(file_name, 'r') as f:
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
                   "16 character display": unit_custom.charOutputUnit,
                   "passthru":unit.PassThruUnit}

def configure_units():
    # Load GUID list from configuration in GUID list
    configuration = load_persistent_configuration("config_test.json")

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

            unit.get_task()
        
        
if __name__ == "__main__": main()



