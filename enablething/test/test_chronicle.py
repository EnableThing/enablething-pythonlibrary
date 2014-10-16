'''
Created on Aug 24, 2014

@author: nick
'''

import time
import uuid
import unittest

from enablething.task import Chronicle
from enablething.jsonschema import ValidationError

class Task(Chronicle):
    def __init__(self):
        self.unit_id = uuid.uuid4().hex
        Chronicle.__init__(self)

class Test_Chronicle(unittest.TestCase):   
    def setUp(self):
        # Test cases of different Chronicle records
        
        self.empty_chronicle = {         "chronicle": []}
        
        self.one_item_chronicle =        {
                                    "chronicle": [
                                        {
                                            "time_ms": 0.3,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 1
                                        }
                                    ]
                                }
        
        self.multiple_item_chronicle =   {
                                    "chronicle": [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 1
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 2
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 3
                                        }
                                    ]
                                }
        
        self.multiple_item_chronicle_return =    {
                                    "chronicle": [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 1
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 2
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 3
                                        },
                                        {
                                            "time_ms": 0.70,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 4
                                        },
                                        {
                                            "time_ms": 0.70,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 5
                                        }
                                    ]
                                }
        
        self.repeated_hop_count_chronicle =   {
                                    "chronicle": [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6a",
                                            "hop": 3
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6b",
                                            "hop": 2
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "3c82ef61-0875-41d3-99ba-101672d79d6c",
                                            "hop": 3
                                        }
                                    ]
                                }
        
        self.loop_chronicle =   {
                                    "chronicle": [
                                        {
                                            "time_ms": 0.2,
                                            "unit_id": "a",
                                            "hop": 1
                                        },
                                        {
                                            "time_ms": 0.30,
                                            "unit_id": "b",
                                            "hop": 2
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "c",
                                            "hop": 3
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "d",
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
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "d",
                                            "hop": 7
                                        },
                                        {
                                            "time_ms": 0.50,
                                            "unit_id": "b",
                                            "hop": 8
                                        }
                                    ]
                                }

    def test_init_no_existing_chronicke(self):
        # Test of __init__ of Chronicle
        # to confirm that the timer starts at initiation.
        test_start_time = time.time()
                    
        task = Task()
        time_diff = task.chronicle_start_time - test_start_time 
        self.assertTrue(time_diff < 0.001)
      
        
    
    def test_isLoop(self):
        # Test of the Chronicle function to check for a 
        # repeating sequence in the chronicle unit_id record.
        
        task = Task()
        task.chronicle = self.loop_chronicle['chronicle'] 
        self.assertTrue(task.isLoop())
        
        task.chronicle = self.multiple_item_chronicle['chronicle']
        self.assertFalse(task.isLoop())
        
        task.chronicle = self.one_item_chronicle['chronicle']
        self.assertFalse(task.isLoop())
        
        task.chronicle = self.empty_chronicle['chronicle']
        self.assertFalse(task.isLoop())
        
    def test_next_neighbour(self):
        # Test of the Chronicle function to return the next neighbour
        # after the current unit ie the neighbour that edited the 
        # chronicle record after unit_id
        
        task = Task()
        
        # Test situation where unit is not in chronicle
        task.unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6a"
        task.chronicle = self.one_item_chronicle['chronicle']
        self.assertRaises(LookupError, lambda: task.next_neighbour())
        
        
        task.unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        task.chronicle = self.one_item_chronicle['chronicle']
        self.assertRaises(LookupError, lambda: task.next_neighbour())
        
        
        task.chronicle = self.multiple_item_chronicle['chronicle']
        self.assertTrue(task.next_neighbour() == "3c82ef61-0875-41d3-99ba-101672d79d6c")
        
        task.chronicle = self.empty_chronicle['chronicle']
        self.assertRaises(LookupError, lambda: task.next_neighbour())
    
        # Now check the algorithm correctly addressed repeated units
        task.chronicle = self.multiple_item_chronicle_return['chronicle']  
        self.assertTrue(task.next_neighbour() == "3c82ef61-0875-41d3-99ba-101672d79d6a")
        
    def test_previous_neighbor(self):
        # Test of the Chronicle function to return the previous neighbour
        # before the current unit ie the neighbour that edited the 
        # chronicle record before unit_id
        task = Task()
        
        # Test situation where unit is not in chronicle
        task.unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6a"
        task.chronicle = self.one_item_chronicle['chronicle']
        self.assertRaises(LookupError, lambda: task.previous_neighbour())
                
        task.unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        task.chronicle = self.one_item_chronicle['chronicle']
        self.assertRaises(LookupError, lambda: task.previous_neighbour())
                
        task.chronicle = self.multiple_item_chronicle['chronicle']
        self.assertTrue(task.previous_neighbour() == "3c82ef61-0875-41d3-99ba-101672d79d6a")
        
        task.chronicle = self.empty_chronicle['chronicle']
        self.assertRaises(LookupError, lambda: task.previous_neighbour())
    
        
        
    def test_add_chronicle(self):
        # Test of the Chronicle function to add a chronicle item
        # when no .chronicle exists.
        task = Task()
        task.chronicle = self.empty_chronicle['chronicle']
        time.sleep(0.05)
        task.add_chronicle()
        for chronicle in task.chronicle:
            self.assertTrue(chronicle['time_ms']>0)
            self.assertTrue("hop" in chronicle) 
            
    def test_extend_chronicle(self):
        # Test of the Chronicle function to add chronicle items when 
        # there is already an existing .chronicle variable.
        
        # Add 50ms on either side of the chronicle definition to make sure the
        # chronicle clock starts at task definition.
        task = Task()
        time.sleep(0.05)
        task.chronicle = self.multiple_item_chronicle['chronicle']
        time.sleep(0.05)
        task.add_chronicle()
        
        for chronicle in task.chronicle:
            self.assertTrue(chronicle['time_ms']>0.10)
            self.assertTrue("hop" in chronicle) 
        
    def test_cost(self):
        task = Task()
        # Test of the Chronicle function to calculate the cost of
        # the Chronicle based on the time elapsed at each hop.
        task.chronicle = self.one_item_chronicle['chronicle']
        task.cost()
        self.assertTrue(task.cost() == 0.30)
        
        task.chronicle = self.multiple_item_chronicle['chronicle']
        task.cost()
        self.assertTrue(task.cost() == 1.00)
        
        task.chronicle = self.empty_chronicle['chronicle']
        task.cost()
        self.assertTrue(task.cost() == 0.00)
    
    def test_validate(self):
        task = Task()
        # Test of the chronicle function to validate that there is a
        # duplicate hop index.
        task.chronicle = self.repeated_hop_count_chronicle['chronicle']
        self.assertRaises(ValidationError, lambda: task.validate_chronicle())
        
    def test_find_units(self):
        task = Task()
        # Test of the chronicle function to validate that there is a
        # duplicate hop index.
        task.unit_id = "3c82ef61-0875-41d3-99ba-101672d79d6b"
        task.chronicle = self.multiple_item_chronicle_return['chronicle']
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
        
        task.chronicle = self.empty_chronicle['chronicle']
        self.assertTrue(task.find_units() == [])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()