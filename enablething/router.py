from collections import defaultdict, OrderedDict
import time

class PheromoneTable(object):
    def __init__(self):
        self.q = 1
        self.min_goodness = 0.001
        self.last_update = None
        self.persistence = 0.001
        self.goodness = defaultdict(dict)
    
    def reinforce(self, destination, neighbour, length):
        # Add Q/L (where L is the number of steps to 
        # the destination or cummulative trip time)
        try:
            self.goodness[destination][neighbour] += q / length
        except KeyError:
            self.goodness[destination][neighbour] = q / length

    def update(self):
        elapsed_time = time.time() - self.last_update
        self.last_update = time.time()

        for destination, value in self.goodness.items():
            c = value
            for neighbour, previous_goodness in c.items():
                print(destination, neighbour, previous_goodness)
                goodness = (1 - self.persistence) ^ (elapsed_time/self.time_increment) * previous_goodness
                if goodness < self.min_goodness:
                    goodness = 0
                matrix_dict[destination][neighbour] = goodness

    def best_neighbour(self, destination):
        min_value = None
        min_key = None
        for key, value in self.goodness[destination].iteritems():
            if min_value == None or value < min_value:
                min_value = value
                min_key = key
        return min_key

    def remove_neighbour(self):
        raise NotImplemented

    def remove_destination(self):
        raise NotImplemented


class NeighbourTable(object):
    def __init__(self):
        self.last_contact = defaultdict(dict)
        self.last_update = None
#     def new(self, destination, neighbour, length):
#         self.last_contact[neighbour] = 0

    def update(self, neighbour):
        if self.last_update == None:
            elapsed_time = 0
        else:
            elapsed_time = time.time() - self.last_update

        self.last_update = time.time()
        
        for existing_neighbour, value in self.last_contact.items():

            self.last_contact[existing_neighbour] += elapsed_time

        
        # Update table to reflect last contact with "neighbour"
        self.last_contact[neighbour] = 0
    
    def debug(self):
        for k,v in self.last_contact.items():
            print k,v

    def remove_neighbour(self):
        # And remove neighbour from pheromone table
        raise NotImplemented

class Chronicle(object):
    # Class to extract and write chronicle to message
    def __init__(self, task):
        self.task = task
        self.chronicle = task.chronicle
        self.start_time = time.time() 
        self.visited_uuids = OrderedDict(dict)
        for key, value in self.chronicle.iteritems():
            if key == "uuid":
                self.visited_uuids.append(value)

    def last(self):
        return self.visited_uuids(-1)
        
    def next(self, current_unit_id):
        # Return the next unit visited after 'current_unit_id'
        index = self.visited_uuids.keys().index(current_unit_id)
        return self.chronicle[index+1]
    
    def previous(self, current_unit_id):
        # Return the previous unit visited before 'current_unit_id'
        # This allows the path back to the originating unit to be traced.
        index = self.visited_uuids.keys().index(current_unit_id)
        return self.chronicle[index-1]
                
    def update(self):
        elapsed_time = time.time() - self.start_time
        updated_chronicle = self.chronicle.append({"uuid":id, "time_ms": elapsed_time})
        self.task.update(chronicle = updated_chronicle)    
    
class Router(object):
    def __init__(self, unit_id):
        self.pheromone = PheromoneTable()
        self.neighbours = NeighbourTable()
        self.unit_id = unit_id
        self.chronicle = None

    def kill(self):
        # Don't pass the packet on
        pass

    def forward(self, destination = None):
        if destination == None:
            pass
            # Multicast to all neighbours, except any addresses in the chronicle
            # Add to pheromone table
        else:
            pass
            # Unicast to destination
        
        raise NotImplemented
        
    def route(self, task):
        # Make sure Router isn't being asked to route a message(task) intended for the host unit
        assert task.to_unit <> self.unit_id
        
        self.chronicle = Chronicle(task)
        
        # This procedure is called when a message (task) is received that isn't for this unit
        # If any routable message received, then update pheromone table
        # This will reduce all pheromone values globally
        self.pheromone.update()

        # Update the Neighbours table, either with a new neighbour
        # or with communication from an existing neighbour
        self.neighbours.update(self.neighbours.immediate)
        
        # Forwards ant
        if task.response == {}:
            # Receive a message addressed to destination d (with no response):
            # This is a "forwards" ant because there it has no response package
            # It is trying to get to to_unit
            
            # Add node i to message chronicle
            # Broadcast to best goodness neighbour or multicast if this is a new destination
            try:
                self.forward(self.pheromone.best_neighbour(self.to_unit))
            except KeyError:
                # Not found, so multi-cast to all units
                self.forward()
        
        if task.response <> {}:                 
            # Backwards ant
            # Receive a message addressed to destination d (with a response):
            # This is a "backwards" ant
            # Retracing its steps following the chronicle
            
            # Extract the neighbour (j) and the <to> address (destination)
            # because we need this to update the pheromone table
            # Reinforce pheromone table T goodness for neighbour, destination
            destination = self.task.to_unit
            neighbour = self.neighbours.last()
            self.pheromone.update(destination, neighbour)
            
            # Forward the message (task) onto the previous unit in the chronicle list
            self.forward(self.chronicle.previous(self.unit_id))

        # Kill old ants
        # If message chronicle time > death_time: then do not pass message on
        
def main():
    pass
    

if __name__ == "__main__": main()