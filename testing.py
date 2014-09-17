'''
Created on Aug 28, 2014

@author: nick
'''

import unit
import json


t = unit.Taskboard()

command = {"test":"test"}

x = t.request("",json.dumps(command))


