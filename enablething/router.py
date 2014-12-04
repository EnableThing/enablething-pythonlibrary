from collections import defaultdict, OrderedDict
import time
import random

from task import Task
from taskboard import Taskboard
from unit import NeighbourUnit
from unit import shortid
from enablethingexceptions import TaskError, RouterError
from requests.exceptions import HTTPError

import logging

class Statistics(object):
    def __init__(self):
        self.reset()      
    def reset(self):
        self.start_time = time.time()
        self.transmitted = 0
        self.received = 0
        self.created = 0
    def add_transmit(self):
        self.transmitted = self.transmitted + 1
    def add_receipt(self):
        self.received = self.received + 1
    def add_create(self):
        self.created = self.created + 1
        
class Subscriptions(object):
    def __init__(self, neighbours):
        self.neighbours = neighbours
        #self.post_capable_neighbours = []
        self.tasks = []
    def subscribe_neighbour(self, neighbourunit):
        if neighbourunit.post_capable == False:
            neighbourunit.watch = True
        
        # neighbournode is a reference to a NeighbourUnit object
        #print len(self.neighbours)
        ## Check if the neigbour has already been added
        #for neighbour in self.neighbours:
        #    print "(((",neighbour.unit_id, neighbourunit.unit_id
        #    if neighbour.unit_id == neighbourunit.unit_id:
        #        #raise Exception
        ##        return None
        #print "append", neighbourunit.unit_id
        
        #self.neighbours.append(neighbourunit)
    def unsubscribe_neighbour(self, neighbourunit_id):
        logging.info("Removed %s from subscriptions", neighbourunit_id)
        
        for neighbour in list(self.neighbours):
            if neighbour.unit_id == neighbourunit_id:
                neighbour.watch = False
                #self.post_capable_neighbours.append(neighbour)
                #self.neighbours.remove(neighbour)
        
    def subscribe_task(self,task, neighbourunit):
        # Check if task is already being watched
        for task_check, _neighbour in self.tasks:
            if task_check.task_id == task.task_id:
                return None
        # Check if the neighbour is 'post capable'
        #for neighbour in self.neighbours:
        if neighbourunit.post_capable == True:
            return
            
        self.tasks.append((task, neighbourunit))
    def post_capable(self, neighbour_id):

        for neighbour in self.neighbours:
            if neighbour.unit_id == neighbour_id:
                neighbour.post_capable = True
                return
            
    def unsubscribe_task(self,task):
        for task_lookup, _neighbour in list(self.tasks):
            if task_lookup.task_id == task.task_id:
                self.tasks.remove((task_lookup,_neighbour))
                return
            
    def get_new_tasks(self):
        logging.info("Subscriptions get_new_tasks()")
        new_tasks = []
        for neighbour in self.neighbours:
            logging.info("get_new_tasks() from unit "+neighbour.unit_id[:4])
            if neighbour.watch:
                for task in neighbour.get_new_commands():
                    assert(task.isCommand() == True and not task.isResponse())
                    #self.received.queue(task)
                    new_tasks.append(task)
                for task in neighbour.get_new_responses():
                    assert(task.isResponse() == True)
                    new_tasks.append(task)
                    #self.received.queue(task)
                logging.info("added new tasks")
        
        for (task, neighbour) in self.tasks:
            #assert(task.isResponse() == True)
            task_update = neighbour.get_response(task)
            if task_update != None:
                if task_update.isResponse():
                    new_tasks.append(task)
            #new_tasks.append(neighbour.get_response(task))
                logging.info("task %s neighbour %s", task.task_id, neighbour.unit_id)
                logging.info("task %s", neighbour.unit_id)
        return new_tasks
    def debug(self):
        print "<Subscriptions"
        print "Neighbours        Watch        Post_capable"
        for neighbour in self.neighbours:
            print neighbour.unit_id[:4], neighbour.watch, neighbour.post_capable
        print "tasks"
        for task, neighbour in self.tasks:
            print task.task_id[:4], neighbour.unit_id[:4]
        print ">"
             
class ACOAlgorithm(object):
    def __init__(self):
        self.q = 1000000
        self.min_goodness = 1
        self.max_goodness = 1000
        self.last_update = time.time()
        self.persistence = .05
        self.time_increment = 1
   
    def reinforce(self, task):
        
        try:
            neighbour = self.get_neighbour(task.previous_neighbour)
        except LookupError:
            logging.error("reinforce() neighbour not found")
            return
            
        destination = task.to_unit   
        
        for hop_id in task.bant:
            cost = task.cost_to_unit(hop_id)                
            self.reinforce_destination_neighbour(hop_id, neighbour, cost)
            print "< neighbour", neighbour.unit_id[:4], "destination", hop_id[:4], "> cost", cost

    
    def reinforce_destination_neighbour(self, destination, search_neighbour, length):
        if destination == self.unit_id:
            return
                    
        if length == 0:
            length = 1
        # Add Q/L (where L is the number of steps to 
        # the destination or cummulative trip time)
        print "self.q/length", self.q/length, "length", length
        
        
        for neighbour in self.neighbours:
            if search_neighbour.unit_id == neighbour.unit_id:
                self.modify_destination_goodness(neighbour, destination, self.q/length)

    
    def modify_destination_goodness(self, neighbour, destination, increment):
        # Check that we aren't trying to update pheromone on current node.
        if destination == self.unit_id:
            return
        try:
            neighbour.destination_goodness[destination] += increment
        except KeyError:

            neighbour.destination_goodness[destination] = increment
        
        if neighbour.destination_goodness[destination] < self.min_goodness:
            neighbour.destination_goodness[destination] = self.min_goodness
        
        if neighbour.destination_goodness[destination] > self.max_goodness:
            neighbour.destination_goodness[destination] = self.max_goodness
            
            
    
    def update_pheromone(self):
        # Simulate evaporation.
        # Reduce global pheromone amounts across all neighbours 
        elapsed_time = time.time() - self.last_update
        self.last_update = time.time()
        
        for neighbour in self.neighbours:
            for destination, goodness in neighbour.destination_goodness.iteritems():
                delta_goodness = -1 * (self.persistence) ** (elapsed_time/self.time_increment) * goodness               
                self.modify_destination_goodness(neighbour, destination, delta_goodness)
                
    def build_router_table(self):
        table = []
        for neighbour in self.acceptable_neighbours:
            # Calculate sum pheromone
            sum_pheromone = 0
            for destination, pheromone in neighbour.destination_goodness.iteritems():
                sum_pheromone = sum_pheromone + pheromone
            for destination, pheromone in neighbour.destination_goodness.iteritems():
                probability = pheromone/sum_pheromone
                table.append(neighbour.unit_id, destination.unit_id, probability)
        return table
                
    def best_neighbour(self, destination, nondeterministic = True):
        # epsilon chance of picking a random
        logging.info("best_neigbour()")
        for neighbour in self.acceptable_neighbours:
            assert(neighbour.unit_id != self.unit_id)
        
        l = []
        for neighbour in self.acceptable_neighbours:
            l.append(neighbour.unit_id[:4])
        logging.info("best_neigbour() acceptable neighbours %s", str(l))
         
        max_goodness = None
        best_neighbour = None
        sum_goodness = 0
        probability_table = []
        print len(self.acceptable_neighbours)

        # Check if there are no acceptable neighbours to forward to
        if len(self.acceptable_neighbours) == 0:
            logging.info("Zero acceptable neighbours")
            return None
        # Check if there is only one acceptable nieghbour, use this if there is
        if len(self.acceptable_neighbours) == 1:
            logging.info("One acceptable neighbour")
            return self.acceptable_neighbours[0]       
       
        # If any neighbours are unvisited
        # Check if any neighbours are unvisited.  If so, then do not use best neighbour
#         for neighbour in self.acceptable_neighbours:
#             for destination_id, goodness in neighbour.destination_goodness.iteritems():
#                 if goodness == 0:
#                     return None
        
        for neighbour in self.acceptable_neighbours:
            for destination_id, goodness in neighbour.destination_goodness.iteritems():
                if destination == destination_id:
                    sum_goodness += goodness
                    probability_table.append((neighbour,sum_goodness - goodness, sum_goodness))
                    if max_goodness == None or goodness > max_goodness:
                        max_goodness = goodness
                        best_neighbour = neighbour
        
        if sum_goodness == 0:
            logging.info("Random choice")
            return random.choice(self.acceptable_neighbours)
            
        
        if best_neighbour == None:
            return None
        
        if nondeterministic:
            r = random.uniform(0,sum_goodness)
            for neighbour, start, end in probability_table:
                if r>= start and r< end:
                    self.destination_goodness_table()
                    logging.info("Non-deterministic neighbour = %s", neighbour.unit_id[:4])
                    return neighbour
        else:
            logging.info("Deterministic neighbour = %s", best_neighbour.unit_id[:4])
            return best_neighbour
    
    def max_pheromone(self,destination):
        max_pheromone = 0
        for neighbour in self.acceptable_neighbours:
            for destination, pheromone in neighbour.destination_goodness.iteritems():
                if max_pheromone == None or pheromone > max_pheromone:
                    max_pheromone = pheromone
                    
        return max_pheromone
    
    
    def random_neighbour(self):
       
        try:
            random_neighbour = random.choice(self.acceptable_neighbours)
        except IndexError:
            logging.error("No neighbour found ... currently do nothing... need to address")
            return None
            
        return random_neighbour

    def remove_neighbour(self):
        raise NotImplemented

    def remove_destination(self):
        raise NotImplemented

    def destination_goodness_table(self):
        print "Destination-Goodness table for unit", self.unit_id[:4]
        unique_destinations = []
        unique_neighbours = []
        for neighbour in self.neighbours:
            for destination, goodness in neighbour.destination_goodness.iteritems():
                if destination not in unique_destinations:
                    unique_destinations.append(destination)
                if neighbour.unit_id not in unique_neighbours:
                    unique_neighbours.append(neighbour.unit_id)
        print "%6s" % "n,d",
        for n in unique_destinations:
            print "%6s" % n[:4],
        print 
        for neighbourid in unique_neighbours:
            print "%6s" % neighbourid[:4],
            for neighbour_ in self.neighbours:
                if neighbour_.unit_id == neighbourid:
                    neighbour = neighbour_
                    break     
            a = [None] * (len(unique_destinations))    
            for destination, goodness in neighbour.destination_goodness.iteritems():

                index = unique_destinations.index(destination)
                
                a[index] = goodness
  
            for n in a:   
                if n == None:
                    print "%6s" % ".",
                else:   
                    print "{:6.0f}".format(n),                
            print
                                
                            

  

class NeighbourHandler(object):
    def __init__(self):
        pass

    def remove_neighbour(self):
        # And remove neighbour from pheromone table
        raise NotImplemented

    
class RouterHandler(ACOAlgorithm):
    def __init__(self, unit_id,taskboard, neighbours):
        ACOAlgorithm.__init__(self)
        self.unit_id = unit_id

        self.taskboard = taskboard
        self.received = Taskboard(self.unit_id, 'RX queue')
        self.transmit = Taskboard(self.unit_id, 'TX queue')
        self.transmitted = Taskboard(self.unit_id, 'Sent tasks queue')
        

        self.neighbours = neighbours
        self.acceptable_neighbours = []
        self.subscriptions = Subscriptions(neighbours)
        self.max_ttl = 60*2 *1000 # TTL in seconds
        #self.max_send_retries = 3
        
        self.statistics = Statistics()
        
        self.success = 0
        self.attempts = 0

    def add_neighbour(self, ip, port, neighbour_id):
        # Check if the neighbour is already in the neighbours list
        if self.unit_id == neighbour_id:
            return
        for neighbour in self.neighbours:
            if neighbour.unit_id == neighbour_id:
                return
            
        
        self.neighbours.append(NeighbourUnit(ip, port, neighbour_id,[], self.unit_id))

    def kill(self):
        # Don't pass the packet on
        pass

    def _refresh_acceptable_neighbours(self, task):
        logging.info("_acceptable_neighbours()")
        acceptable_neighbours = []
        
        try:
            previous_neighbour = task.previous_neighbour
        except LookupError:
            previous_neighbour = None
        logging.info("previous neighbour %s", previous_neighbour)    
        # Check to see if any neighbours are unvisited

            
        if self.max_pheromone == 0 and previous_neighbour != neighbour.unit_id:
            acceptable_neighbours.append(neighbour)
            # There is an unvisited neighbour
    
        if acceptable_neighbours == []: 
            for neighbour in self.neighbours:
                if previous_neighbour != neighbour.unit_id:
                    acceptable_neighbours.append(neighbour)
                
                
        self.acceptable_neighbours = acceptable_neighbours


    def _unicast(self, task, unit):
        logging.info("_unicast() to neighbour %s", unit.unit_id[:4])
        unit.post_task(task)
        self.subscriptions.subscribe_task(task, unit)
        
        self.modify_destination_goodness(unit, task.to_unit, self.min_goodness)       
        self.subscriptions.subscribe_neighbour(unit)
       

    def _multicast(self, task, units):
        logging.info("_mulitcast()")
        for unit in units:
            self._unicast(task, unit)

    def _forward_ant(self,task):
        logging.info("_forward_ant() called")  
        # forward ant
        # check pheromone table and route to best neighbour or multicast
        

        for neighbour in self.neighbours:
            neighbour.add_destination(task.to_unit) 
            for chronicle in task.chronicle:
                neighbour.add_destination(chronicle['unit_id']) 
        

        best_neighbour = self.best_neighbour(task.to_unit)
        
#         # Check if any neighbours are unvisited.  If so, then do not use best neighbour
#         for neighbour in self.acceptable_neighbours:
#             for destination_id, goodness in neighbour.destination_goodness.iteritems():
#                 if goodness == 0:
#                     best_neighbour = None
        
        if best_neighbour == None:
            logging.info("_forward_ant will be posted to any neighbour")

            any_neighbour = self.random_neighbour()
            if any_neighbour == None:
                logging.debug("any_neighbour - no neighbours to choose from")
                task.note = "FANT no neighbours"
                raise RouterError
            else:
                #Randomcast
#                 logging.debug("any_neighbour.post_task(task) %s", task.task_id)
#                 any_neighbour.post_task(task)
#                 
#                 for neighbour in self.neighbours:
#                     if neighbour.unit_id == any_neighbour.unit_id:
#                         neighbour.destination_goodness[task.to_unit] = self.min_goodness
                
                logging.info("_forward_ant posted to anyneighbour %s", any_neighbour.unit_id)
                
                self._multicast(task, self.acceptable_neighbours)                   
                task.note = "FANT multicast"
                task.status = "Completed"    
                
            # Need to consider whether a random walk or multi-cast is "better"
        else:
            logging.info("Unicast- to best neighbour %s", best_neighbour.unit_id[:4])

            self._unicast(task, best_neighbour)

            task.note = "FANT unicast best "+ best_neighbour.unit_id[:4]
            task.status = "Completed"    


    def _backward_ant(self, task):
        logging.info("_backward_ant() called")
        self.subscriptions.unsubscribe_task(task)
        
        #if task.from_unit != self.unit_id:
        for neighbour in self.neighbours:
            neighbour.add_destination(task.from_unit)

        neighbour_id = None      
#         try:
        print "unit id", self.unit_id
        task.get_next_neighbour()
        neighbour_id = task.next_neighbour
        try:
            neighbour = self.get_neighbour(neighbour_id) 
        except LookupError:
            task.debug()
            logging.error("LookupError _backward_ant() chronicle")
 
            task.note = "BANT neighbour not found"
            raise RouterError

            
        
        self.destination_goodness_table()

        if task.isResponse() and task.from_unit == self.unit_id:
            # This task has completed it's trip.
            task.note = "BANT received by unit"+self.unit_id[:4]
            self.taskboard.queue(task)
        else:
            try:
                neighbour.post_task(task)
            except HTTPError:
                raise RouterError("HTTP Error could not post task")
            
            self.subscriptions.subscribe_neighbour(neighbour)
            logging.info("_backward_ant posted to %s", neighbour.unit_id)
            '''delete message from taskboard'''
            task.note = "BANT posted "+ neighbour.unit_id[:4]
            task.status = "Completed"
        

    
    def get_neighbour(self, unit_id):
        for neighbour in self.neighbours:
            if neighbour.unit_id == unit_id:
                return neighbour
        raise LookupError("Neighbour "+unit_id[:4] +" not found in neighbours")

    def add_neighbour_from_task(self, task):
        
        try:   
            previous_neighbour_id = task.previous_neighbour
            if previous_neighbour_id == self.unit_id:
                return
            for neighbour in self.neighbours:
                if previous_neighbour_id == neighbour.unit_id:
                    # Already known
                    return    
        except LookupError:
            return
            
        ip = "127.0.0.1"
        self.neighbours.append(NeighbourUnit(ip, previous_neighbour_id, []))
        self.update_router()
        print "Neighbour added from task"



    def update_router(self):
        #self.transmit.debug()
        #self.received.debug()
        # Process received queue

        # If any message received, then update pheromone table
        # This will reduce all pheromone values globally
        self.update_pheromone()

        self.process_received()
        self.process_transmit()
        
        #self.transmit.debug()
        #raw_input("wait")

    def process_received(self):
        logging.info("process_received()")
        discover_neighbours = False
        task = self.received.next()
        if task != None:
            logging.info("task.previous_neighbour %s self.unit_id %s", shortid(task.previous_neighbour), shortid(self.unit_id))
            #assert(task.previous_neighbour != self.unit_id)
            
            #for task in list(self.received.tasks):
            if discover_neighbours:
                self.add_neighbour_from_task(task)
                
            if task.isLoop():
                logging.info("Loop removed")
                task.note = "Loop removed"
                task.remove_loop()
            
            if task.cost() > self.max_ttl:
                # Exceed TTL, so kill task
                task.note = "Exceeded TTL"
                task.status = "Terminated"
                                
            elif task.from_unit == self.unit_id and task.isResponse():
                task.note = "Response recd from RX"
                self.taskboard.queue(task)
            elif task.to_unit == self.unit_id and task.isCommand():
                # Addressed to this unit
                task.note = "Command recd from RX"
                self.taskboard.queue(task)
            else:
                # Route directly from received queue to transmit queue
                task.note = "Task moved to TX from RX"
                #self.transmit.queue(task)
                try:
                    logging.info("self.route_task(task)")
                    self.route_task(task)
                except RouterError:
                    logging.error("Unable to route task")
            
            #self.transmitted.dequeue(task)
            #self.success = self.success + 1
        
            self.statistics.add_receipt()
            
            self.received.dequeue(task)

#     def retriesExceeded(self, task):
#         if task.send_retries >= self.max_send_retries:
#             try:
#                 for taskset in list(self.taskboard.tasksets):
#                     for t in taskset.tasks:
#                         if t.task_id == task.task_id:
#                             self.taskboard.tasksets.remove(taskset)            
#                             raise LookupError
#             except LookupError:
#                 task.note = "Retries exceeded"
#                 #self.taskboard.dequeue(task)
#                 #raise Exception
#                 #logging.error("Retries exceed - remove task")
#             return True
#         else:
#             return False        

    def process_transmit(self):
        logging.info("process_transmit()")
        task = self.transmit.next()

        if task != None:
            assert(task.previous_neighbour != self.unit_id)
            
#             if self.retriesExceeded(task):
#                 task.note = "Retries exceeded."
#                 task.status = "Terminated"
#                     
#             else:
            task.send_retries += 1
            try:
                self.route_task(task)
                self.statistics.add_transmit()
            except RouterError:
                logging.error("Unable to route task")
                
            self.transmit.dequeue(task)
        
                
    def route_task(self,task):

        logging.info("route_task() %s", task.task_id[:4])
        logging.debug("unit_id %s", self.unit_id[:4])
        #assert(isinstance(task,Task))
        

            
        # Acceptable tasks for route_task
        # (a) where current unit is to_unit and has a response: this is a response on it's way back to from_unit
        # (b) where current unit is from_unit and has a command: this is a new response on it's way to from_unit
        
     
         
        if task != None:
            # Find out where the message came from and
            # update the Neighbour table.
            # Even if it comes from 'radio' the unit sending it is a neighbour
            discover_neighbours = False
            if discover_neighbours:
                try:
                    neighbour_id = task.previous_neighbour
                    neighbour = self.get_neighbour(neighbour_id)
                    neighbour.update()
                except LookupError:
                    # No basis for deciding where the message came from
                    # so assume this is a forward ant.
                    pass
            
            logging.debug("check ttl... task.cost %s", task.cost())
    
            # Update the list of the neighbours it is acceptable to forward this task to.
            self._refresh_acceptable_neighbours(task)
     
            if task.isResponse():
                self.reinforce(task)
                self._backward_ant(task)
            elif task.isCommand() and not task.isResponse():
                self._forward_ant(task)
            else:
                raise RouterError("Undefined situation")
        

def main():
    pass
    

if __name__ == "__main__": main()