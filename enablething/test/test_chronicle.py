'''
Created on Aug 24, 2014

@author: nick
'''

import time
import uuid
import unittest

from enablething.task import Chronicle
from enablething.jsonschema import ValidationError
from enablething.enablethingexceptions import TaskError
#from enablething.task import Task

def create_task(chronicle = [], unit_id = None, from_unit = None, to_unit = None):
    
    print "hello"
    if unit_id ==None:
        unit_id = uuid.uuid4().hex
    
    if to_unit == None:
        to_unit = uuid.uuid4().hex
    if from_unit == None:
        from_unit = uuid.uuid4().hex
    return Task(unit_id, 
                to_unit = to_unit, 
                from_unit = from_unit,
                command = {"output":{}},
                chronicle = chronicle
                )

class Task(Chronicle):
    def __init__(self, unit_id, **kwargs):
        self.unit_id = unit_id
        options = {
            'task_id' : "",
            'board' : 'Backlog',
            'command' : {},
            'response' : {},
            'chronicle' : []
            }

        options.update(kwargs)
        for key, value in options.iteritems():
            setattr(self,key, value)
        print "self.chronicle", self.chronicle  
        #assert(self.to_unit != None)
        Chronicle.__init__(self,self.to_unit)   

class Test_Chronicle(unittest.TestCase):   
    def setUp(self):
        # Test cases of different Chronicle records
        
        self.empty_chronicle = []
        
        self.one_item_chronicle =        [
                                        {
                                            "time_ms": 0.3,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 0
                                        }
                                    ]
                                
        
        self.multiple_item_chronicle =   [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 0
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 1
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 2
                                        }
                                    ]
                                
            
        self.alt_multiple_item_chronicle =   [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 0
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 1
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 2
                                        },
                                        {
                                            "time_ms": 0.70,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6d",
                                            "hop": 3
                                        },
                                        {
                                            "time_ms": 1.10,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6e",
                                            "hop": 4
                                        },
                                        {
                                            "time_ms": 1.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6d",
                                            "hop": 5
                                        },
                                        {
                                            "time_ms": 1.70,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 6
                                        }
                                    ]
                                
        
        self.multiple_item_chronicle_return =    [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 0
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 1
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 2
                                        },
                                        {
                                            "time_ms": 0.70,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 3
                                        },
                                        {
                                            "time_ms": 0.70,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 4
                                        }
                                    ]
                                
        
        self.repeated_hop_count_chronicle =   [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 0
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 2
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 2
                                        }
                                    ]
                                
        
        self.loop_chronicle =   [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "a",
                                            "hop": 1
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "b",
                                            "hop": 1
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "c",
                                            "hop": 2
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "d",
                                            "hop": 3
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "e",
                                            "hop": 4
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "b",
                                            "hop": 5
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "c",
                                            "hop": 6
                                        }
                                    ]
                                
        
        self.loop_chronicle_w_loop_removed =   [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "a",
                                            "hop": 1
                                        }
                                ]
                            
        
        
        self.alt_loop_test = [
                                            {
                                              "time_ms":17.0,
                                              "unit_id":"d57c1438-2373-4448-8c23-0bd7ad034d6a",
                                              "hop":0
                                            },
                                            {
                                              "time_ms":19.0,
                                              "unit_id":"3c82ef61-0875-41d3-99ba-101672d79d6b",
                                              "hop":1
                                                                                          },
                                            {
                                              "time_ms":18.0,
                                              "unit_id":"caf01485-3bb1-4337-a023-5ffc03bf073b",
                                              "hop":2
                                            },
                                            {
                                              "time_ms":456.0,
                                              "unit_id":"3c82ef61-0875-41d3-99ba-101672d79d6b",
                                              "hop":3
                                            }
                                          ]
                              
        
        self.loop_test_real_1 = [{u'time_ms': 2871.0, u'unit_id': u'd57c1438-2373-4448-8c23-0bd7ad034d6a', u'hop': 0}, {u'time_ms': 1811.0, u'unit_id': u'caf01485-3bb1-4337-a023-5ffc03bf073b', u'hop': 1}, {u'time_ms': 1837.0, u'unit_id': u'caf01485-3bb1-4337-a023-5ffc03bf073b', u'hop': 2}, {u'time_ms': 1190.0, u'unit_id': u'a789ada1-edb5-4cfe-b1f9-8584abbf8a2f', u'hop': 3}, {u'time_ms': 1168.0, u'unit_id': u'3c82ef61-0875-41d3-99ba-101672d79d6b', u'hop': 4}, {u'time_ms': 2430.0, u'unit_id': u'd57c1438-2373-4448-8c23-0bd7ad034d6a', u'hop': 5}, {u'time_ms': 2446.0, u'unit_id': u'd57c1438-2373-4448-8c23-0bd7ad034d6a', u'hop': 6}, {u'time_ms': 1278.0, u'unit_id': u'caf01485-3bb1-4337-a023-5ffc03bf073b', u'hop': 7}]
                                 
        self.loop_test_real_1_no_loop = [{u'time_ms': 2871.0, u'unit_id': u'd57c1438-2373-4448-8c23-0bd7ad034d6a', u'hop': 0}, {u'time_ms': 1811.0, u'unit_id': u'caf01485-3bb1-4337-a023-5ffc03bf073b', u'hop': 1}, {u'time_ms': 1837.0, u'unit_id': u'caf01485-3bb1-4337-a023-5ffc03bf073b', u'hop': 2}, {u'time_ms': 1190.0, u'unit_id': u'a789ada1-edb5-4cfe-b1f9-8584abbf8a2f', u'hop': 3}, {u'time_ms': 1168.0, u'unit_id': u'3c82ef61-0875-41d3-99ba-101672d79d6b', u'hop': 4}, {u'time_ms': 2430.0, u'unit_id': u'd57c1438-2373-4448-8c23-0bd7ad034d6a', u'hop': 5}, {u'time_ms': 2446.0, u'unit_id': u'd57c1438-2373-4448-8c23-0bd7ad034d6a', u'hop': 6}, {u'time_ms': 1278.0, u'unit_id': u'caf01485-3bb1-4337-a023-5ffc03bf073b', u'hop': 7}]
                                 
    def test_init_chronicle(self):
        task = create_task(self.multiple_item_chronicle)
        self.assertTrue(len(task.chronicle) == 3 + 1)
        
    def test_init_case2(self):
        # No existing chronicle
        # Test of __init__ of Chronicle
        # to confirm that the timer starts at initiation.
        test_start_time = time.time()
                    
        task = create_task(chronicle = [])
        time_diff = task.chronicle_start_time - test_start_time 
        self.assertTrue(time_diff < 0.001)
        
    def test_visited_units(self):
        task = create_task(chronicle = self.alt_multiple_item_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b", to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6e")
        print "task.visited_units", task.visited_units
        expected_result = ["3c82ef61-0875-41d3-99ba-101672d79d6a",
                           "3c82ef61-0875-41d3-99ba-101672d79d6b",
                           "3c82ef61-0875-41d3-99ba-101672d79d6c",
                           "3c82ef61-0875-41d3-99ba-101672d79d6d",
                           "3c82ef61-0875-41d3-99ba-101672d79d6e",
                           "3c82ef61-0875-41d3-99ba-101672d79d6d",
                           "3c82ef61-0875-41d3-99ba-101672d79d6c",
                           "3c82ef61-0875-41d3-99ba-101672d79d6b"]
        
        self.assertTrue(task.visited_units == expected_result)
        
    def test_fant(self):
        task = create_task(chronicle = self.multiple_item_chronicle_return, to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        print "task.visited_units", task.visited_units
        expected_result = ["3c82ef61-0875-41d3-99ba-101672d79d6a",
                           "3c82ef61-0875-41d3-99ba-101672d79d6b",
                           "3c82ef61-0875-41d3-99ba-101672d79d6c"]
        print task.fant
        self.assertTrue(task.fant == expected_result)
       
       
        task = create_task(chronicle = self.multiple_item_chronicle, to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        print "task.visited_units", task.visited_units
        expected_result = ["3c82ef61-0875-41d3-99ba-101672d79d6a",
                           "3c82ef61-0875-41d3-99ba-101672d79d6b",
                           "3c82ef61-0875-41d3-99ba-101672d79d6c"]
        print task.fant
        self.assertTrue(task.fant == expected_result)
       
        task = create_task(chronicle = [], unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6a" ,to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        print "task.visited_units", task.visited_units
        expected_result = ["3c82ef61-0875-41d3-99ba-101672d79d6a"]
        print task.fant
        self.assertTrue(task.fant == expected_result)      
            
    def test_bant(self):
        task = create_task(chronicle = self.multiple_item_chronicle_return, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6q",
                           to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        print "task.visited_units", task.visited_units
        print task.bant
        expected_result = ["3c82ef61-0875-41d3-99ba-101672d79d6c",
                           "3c82ef61-0875-41d3-99ba-101672d79d6b",
                           "3c82ef61-0875-41d3-99ba-101672d79d6a",
                           "3c82ef61-0875-41d3-99ba-101672d79d6q"]
        self.assertTrue(task.bant == expected_result)
                                     
        task = create_task(chronicle = self.multiple_item_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b", to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        
        expected_result = ['3c82ef61-0875-41d3-99ba-101672d79d6c', 
                           '3c82ef61-0875-41d3-99ba-101672d79d6b']
        print "task.visited_units", task.visited_units
        print "task.fant", task.fant
        print "task.bant", task.bant
        self.assertTrue(task.bant == expected_result)
        
        task = create_task(chronicle = [], unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6a", to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        print "task.visited_units", task.visited_units
        expected_result = []
        print task.bant
        self.assertTrue(task.bant == expected_result)
        
    def test_next_neighbour_case1(self):
        task = create_task(chronicle = self.alt_multiple_item_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6e", to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6e")
        print "task.visited_units", task.visited_units
        print "task.fant", task.fant
        print "task.bant", task.bant
        print "task.next_neighbour", task.next_neighbour
        print "task.previous_neighbour", task.previous_neighbour
        self.assertTrue(task.next_neighbour == "3c82ef61-0875-41d3-99ba-101672d79d6a")
        
    def test_next_neighbour_case2(self):
        task = create_task(chronicle = self.multiple_item_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b", to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        print "task.visited_units", task.visited_units
        print "task.fant", task.fant
        print "task.bant", task.bant
        print "task.next_neighbour", task.next_neighbour
        print "task.previous_neighbour", task.previous_neighbour
        self.assertTrue(task.next_neighbour == "3c82ef61-0875-41d3-99ba-101672d79d6a")

    def test_previous_neighbour_case1(self):
        task = create_task(chronicle = [], unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b", to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        print "task.visited_units", task.visited_units
        print "task.fant", task.fant
        print "task.bant", task.bant
        print "task.next_neighbour", task.next_neighbour
        print "task.previous_neighbour", task.previous_neighbour
        self.assertTrue(task.previous_neighbour == None)
        
    def test_previous_neighbour_case2(self):
        task = create_task(chronicle = self.one_item_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6c", to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        print "task.visited_units", task.visited_units
        print "task.fant", task.fant
        print "task.bant", task.bant
        print "task.next_neighbour", task.next_neighbour
        print "task.previous_neighbour", task.previous_neighbour
        self.assertTrue(task.previous_neighbour == "3c82ef61-0875-41d3-99ba-101672d79d6b")
  
    def test_previous_neighbour_case3(self):
        task = create_task(chronicle = self.multiple_item_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b", to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6c")
        print "task.visited_units", task.visited_units
        print "task.fant", task.fant
        print "task.bant", task.bant
        print "task.next_neighbour", task.next_neighbour
        print "task.previous_neighbour", task.previous_neighbour
        self.assertTrue(task.previous_neighbour == "3c82ef61-0875-41d3-99ba-101672d79d6c")
    
    def test_isLoop(self):
        # Test of the Chronicle function to check for a 
        # repeating sequence in the chronicle unit_id record.
        
        task = create_task(chronicle = self.loop_chronicle, unit_id = "d")
        print "task.fant",task.fant
        print "task.bant",task.bant
        print "task.isLoop()", task.isLoop()
        
        #task.chronicle = self.loop_chronicle['chronicle'] 
        self.assertTrue(task.isLoop())
        
        task = create_task(self.multiple_item_chronicle)
        #task.chronicle = self.multiple_item_chronicle['chronicle']
        self.assertFalse(task.isLoop())
        
        task = create_task(self.one_item_chronicle)
        #task.chronicle = self.one_item_chronicle['chronicle']
        self.assertFalse(task.isLoop())
        
        task = create_task(self.empty_chronicle)
        #task.chronicle = self.empty_chronicle['chronicle']
        self.assertFalse(task.isLoop())
        
        task = create_task(self.alt_loop_test)
        #task.chronicle = self.alt_loop_test['chronicle']
        
        self.assertFalse(task.isLoop())
        

 
        
    def test_close_chronicle_case1(self):
        # Test of the Chronicle function to add a chronicle item
        # when no .chronicle exists.
        neighbour = uuid.uuid4().hex
        
        task = create_task(chronicle = self.empty_chronicle)
        time.sleep(0.05)
        task.close_chronicle()
        task.chronicle_debug()
        
        print "task.chronicle",task.chronicle
         
        self.assertTrue(task.chronicle[-1]['hop'] == 0)
                
        for chronicle in task.chronicle:
            self.assertTrue(chronicle['time_ms']>0)
            self.assertTrue("hop" in chronicle)
        
        # Change the unit_id so we can add a new task. 
        task.unit_id = uuid.uuid4().hex
            
        self.assertRaises(TaskError, lambda: task.close_chronicle())

    def test_close_chronicle_case2(self):
        # Test of the Chronicle function to add a chronicle item
        # when no .chronicle exists.
        neighbour = uuid.uuid4().hex
        
        task = create_task(chronicle = self.multiple_item_chronicle)
        task.close_chronicle()
 
        self.assertTrue(task.chronicle[-1]['hop'] == 3)
            
        self.assertRaises(TaskError, lambda: task.close_chronicle())          
            
    def test_extend_chronicle_case1(self):
        
        #chronicle = [{u'time_ms': 12.0, u'unit_id': u'6d66ed56407042509eedecc2d8626540', u'hop': 0}, {'time_ms': 151.0, 'unit_id': '526188516f1343c79531706a6a6a0002', 'hop': 0}]
        chronicle = [{u'time_ms': 12.0, u'unit_id': u'6d66ed56407042509eedecc2d8626540', u'hop': 0}]
        task = create_task(chronicle = chronicle)
        task.close_chronicle()
        self.assertTrue(task.chronicle[-1]['hop'] == 1)
        
    def test_extend_chronicle_case2(self):
        # Test of the Chronicle function to add chronicle items when 
        # there is already an existing .chronicle variable.
        
        # Add 50ms on either side of the chronicle definition to make sure the
        # chronicle clock starts at task definition.
        task = create_task()
        time.sleep(0.05)

        task.chronicle = self.multiple_item_chronicle
        task.load()
        task.update()
        
        time.sleep(0.05)
        task.unit_id = uuid.uuid4().hex
        task.close_chronicle()

        for chronicle in task.chronicle:
            self.assertTrue(chronicle['time_ms']>0.10)
            self.assertTrue("hop" in chronicle) 
  
    def test_cost_to_unit(self):
        task = create_task(chronicle = self.alt_multiple_item_chronicle, to_unit = "3c82ef61-0875-41d3-99ba-101672d79d6e")
        print "fant", task.fant
        print "bant", task.bant
        
        self.assertTrue(task.cost_to_unit("3c82ef61-0875-41d3-99ba-101672d79d6d")== 1.8)
                        
        self.assertTrue(task.cost_to_unit("3c82ef61-0875-41d3-99ba-101672d79d6e")== 1.10)
        self.assertTrue(task.cost_to_unit("3c82ef61-0875-41d3-99ba-101672d79d6c")== 2.3)
        self.assertTrue(task.cost_to_unit("3c82ef61-0875-41d3-99ba-101672d79d6b")== 2.6)
        
        '''[
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 0
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 1
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 2
                                        },
                                        {
                                            "time_ms": 0.70,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6d",
                                            "hop": 3
                                        },
                                        {
                                            "time_ms": 1.10,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6e",
                                            "hop": 4
                                        },
                                        {
                                            "time_ms": 1.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6d",
                                            "hop": 5
                                        },
                                        {
                                            "time_ms": 1.70,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 6
                                        }
                                    ]'''
                    
        
    def test_cost(self):
        task = create_task(self.one_item_chronicle)
        print task.cost()
        self.assertTrue(task.cost() == 0.30)
        
        task = create_task(self.multiple_item_chronicle)
        print task.cost()
        self.assertTrue(task.cost() == 1.00)
        
        task = create_task(chronicle = self.empty_chronicle)
        print task.cost()
        self.assertTrue(task.cost() == 0.00)
        
        task = create_task(chronicle = [])
        print task.cost()
        self.assertTrue(task.cost() == 0.00)
    
    def test_validate(self):
        task = create_task(chronicle = self.repeated_hop_count_chronicle)
        task.task_id = uuid.uuid4().hex
        self.assertRaises(ValidationError, lambda: task.validate_chronicle())
        
    def test_find_units(self):
        task = create_task(self.multiple_item_chronicle_return, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b")
        
        unexpected_result = ["3c82ef61-0875-41d3-99ba-101672d79d6a",
                           "3c82ef61-0875-41d3-99ba-101672d79d6b",
                           "3c82ef61-0875-41d3-99ba-101672d79d6c",
                           "3c82ef61-0875-41d3-99ba-101672d79d6b",
                           "3c82ef61-0875-41d3-99ba-101672d79d6a"]
        self.assertFalse(task.find_units() == unexpected_result)
        # But this is telling us about units other than the current unit,
        # so that they can be tested for contact-ability.
        # SO we are looking for:
        expected_result = ["3c82ef61-0875-41d3-99ba-101672d79d6a",
                           "3c82ef61-0875-41d3-99ba-101672d79d6c",
                           "3c82ef61-0875-41d3-99ba-101672d79d6a"]
        self.assertTrue(task.find_units() == expected_result)
        
        task = create_task(self.empty_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b")
        
        self.assertTrue(task.find_units() == [])

    def test_get_hop_from_unit(self):
        task= Task()
        task.unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        print "test_neighbour_destination_cost()"
        task.chronicle = self.multiple_item_chronicle_return['chronicle']

        print task.get_hop_from_unit(task.unit_id)
        self.assertTrue(task.get_hop_from_unit(task.unit_id) == [1,3])
        
        
        task.chronicle = self.empty_chronicle['chronicle']
        self.assertRaises(LookupError, lambda: task.get_hop_from_unit(task.unit_id))
        
        task.chronicle = self.one_item_chronicle['chronicle']
        self.assertTrue(task.get_hop_from_unit(task.unit_id) == [0])

    def test_get_unit_from_hop(self):
        task= Task()
        task.unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        print "test_neighbour_destination_cost()"
        task.chronicle = self.multiple_item_chronicle_return['chronicle']

        print task.get_hop_from_unit(task.unit_id)
        self.assertTrue(task.get_unit_from_hop(1) == '3c82ef61-0875-41d3-99ba-101672d79d6b')
        
        
        task.chronicle = self.empty_chronicle['chronicle']
        self.assertRaises(LookupError, lambda: task.get_unit_from_hop(0))
        
        task.chronicle = self.one_item_chronicle['chronicle']
        self.assertTrue(task.get_unit_from_hop(0) == '3c82ef61-0875-41d3-99ba-101672d79d6b')

    def test_current_hop(self):
        task = create_task(chronicle = self.multiple_item_chronicle_return, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b")

        print task.current_hop
        self.assertTrue(task.current_hop == 5)
        
        task = create_task(chronicle = self.one_item_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b")
        self.assertTrue(task.current_hop == 1)
        
        task = create_task(chronicle = self.empty_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b")
        self.assertTrue(task.current_hop == 0)
        
 
    def test_remove_loop(self):
        task= create_task(self.loop_chronicle, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b")
        
        print "before", task.chronicle
        task.remove_loop()
        print "after", task.chronicle
        print "compare to", self.loop_chronicle_w_loop_removed
        self.assertTrue(task.chronicle == self.loop_chronicle_w_loop_removed)

        task= create_task(self.loop_test_real_1, unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b")
        
        task.remove_loop()

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()