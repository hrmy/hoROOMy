import os
from time import time, ctime

root = "logs"

tab = chr(9)

def log(message, head = '', _print = False):
    message = str(message)

    if (_print):
        print(message)

    message = ctime(time()) + tab + head + ':' + tab + message + '\n'

    with open(root+'/randomproxy.log', 'a') as logfile:
        logfile.write(message)


def clearlog():
    with open(root+'/randomproxy.log', 'w') as logfile:
        a = 1
    log('logfile cleared')
