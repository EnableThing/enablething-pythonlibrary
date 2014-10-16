from collections import defaultdict, OrderedDict
import time

class PheromoneTable(object):
    def __init__(self):
        self.q = 1
        self.min_goodness = 0.001
        self.last_update = time.time()
        self.persistence = 0.001
        self.goodness = defaultdict(dict)
    
    def reinforce(self, destination, neighbour, length):
        if length == 0:
            return
        # Add Q/L (where L is the number of steps to 
        # the destination or cummulative trip time)
        try:
            self.goodness[destination][neighbour] += self.q / length
        except KeyError:
            self.goodness[destination][neighbour] = self.q / length

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

    
class RouterHandler(object):
    def __init__(self, unit_id,taskboard):
        self.pheromone_table = PheromoneTable()
        self.neighbour_table = NeighbourTable()
        self.unit_id = unit_id
        #self.chronicle = None
        self.taskboard = taskboard


    def kill(self):
        # Don't pass the packet on
        pass

    def _forward_ant(self,task):
        # forward ant
        # check pheromone table and route to best neighbour or multicast
        try:
            self.forward(self.pheromone_table.best_neighbour(task.to_unit))
        except KeyError:
            # Not found, so multi-cast to all units
            self.forward()

    def _backward_ant(self,task):
        # 'backward ant' retracing its steps
        # check chronicle and route back along route
        neighbour = task.chronicle_manager.previous(self.unit_id)
        print "neighbour", neighbour
        destination = task.to_unit

        # Reinforce pheromone table T goodness for neighbour, destination
        
        # Calculate length
        time_ms = task.chronicle_manager.length()
        
        self.pheromone.reinforce(destination, neighbour, time_ms)
        '''delete message from taskboard'''

    def route_task(self,task):
        if task.response == {}:
            self._forward_ant(task)
        else:
            self._backward_ant(task)
            
    

    def process_task(self, task):
        print "process_task"
        print "task>", task.json()
        
        #task = self.incoming()
        if task == None:
            return
        
        # If any message received, then update pheromone table
        # This will reduce all pheromone values globally
        self.pheromone_table.update()

        # Find out where the message came from and
        # update the Neighbour table.
        # Even if it comes from 'radio' the unit sending it is a neighbour
        try:
            neighbour = task.previous_neighbour()
            self.neighbour_table.update(neighbour)
        except LookupError:
            pass

        # Debatable: TTL kill messages if they are too old.
        # Try initially setting TTL to 10 minutes
        '''if chronicle life > TTL:
            return'''

        print "taskboard"
        self.taskboard.debug()
        if task.to_unit == self.unit_id or task.from_unit == self.unit_id:
            '''add message to task board'''
            # By adding message to task board, unit will process messages addressed
            # to it, so no further action needed to "process" message here.
            try:

                self.taskboard.respond(task)
                print "Task found"
                
                #return request.response(("Task "+ task.task_id + "updated successfully"))
            except (LookupError, ValueError):
                # Means that an existing task was not found
                print "Task not found"
                self.taskboard.add(task)
                #return request.response(("Task " + task.task_id + "added"))
        else:
            ''' if message is not addressed to this unit:
                append chronicle
                route message  '''
            task.chronicle.add_chronicle()
            
            self.route_message(task)
    























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