from time import time, ctime

tab = chr(9)


def log(message, head = '', _print = False):
    message = str(message)

    if (_print):
        print(message)

    message = ctime(time()) + tab + head + ':' + tab + message + '\n'

    with open('randomproxy/log.txt', 'a') as logfile:
        logfile.write(message)


def clearlog():
    with open('randomproxy/log.txt', 'w') as logfile:
        a = 1
    log('logfile cleared')
