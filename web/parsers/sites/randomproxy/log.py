import os
from time import time, ctime

os.chdir(os.path.dirname(__file__))

tab = chr(9)

def log(message, head = '', _print = False):
    message = str(message)

    if (_print):
        print(message)

    message = ctime(time()) + tab + head + ':' + tab + message + '\n'

    with open('log.txt', 'a') as logfile:
        logfile.write(message)


def clearlog():
    with open('log.txt', 'w') as logfile:
        a = 1
    log('logfile cleared')
