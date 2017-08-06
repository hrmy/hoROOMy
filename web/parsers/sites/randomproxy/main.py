import requests
from random import choice
import os

root = os.path.dirname(__file__)

def get_proxy():

    with open(root+'/http_proxies.txt', 'r') as f:
        http_proxies = f.read().split('\n')
    with open(root+'/https_proxies.txt', 'r') as f:
        https_proxies = f.read().split('\n')

    proxy = {'http': 'http://' + choice(http_proxies),
             'https': 'https://' + choice(https_proxies)}
    return proxy


def get_useragent():

    with open(root+'/headers.txt', 'r') as f:
        useragents = f.read().split('\n')

    useragent = {'User-Agent': choice(useragents)}
    return useragent


def make_request(url, rtype = 'get', data = None, headers = None, proxies = None, timeout = None):
    if (rtype == 'get'):
        r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        return r

    elif(rtype == 'post'):
        r = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=timeout)
        return r


def getpost(url, rtype = 'get', data = None):
    url = str(url)
    print('GET ' + url)

    times = 0
    maxtimes = 12
    timeout = 15

    while times <= maxtimes:
        times += 1

        try:
            proxy = get_proxy()
            useragent = get_useragent()
        except Exception as exc:
            print(str(exc))
            continue

        print('proxy = ' + str(proxy))
        print('useragent = ' + str(useragent))

        try:
            r = make_request(url, rtype=rtype, data=data, headers=useragent, proxies=proxy, timeout=timeout)
            if (r.status_code == 200):
                print('success')
                return r
            else:
                print('Unsuccess. Request is done, but status code is %d' % r.status_code)
        except Exception as exc:
            print(str(exc))
            print('unsuccess')

        #log('', _print=True)

    print('proxy did not work %d times, returning request made only with headers' % maxtimes)

    try:
        useragent = get_useragent()
        r = make_request(url, rtype=rtype, data=data, headers=useragent)
        return r
    except Exception as exc:
        print(str(exc))
        print('request caused an error, returning None')
        return exc


def get(url):
    return getpost(url, rtype = 'get')


def post(url, data):
    return getpost(url, rtype = 'post', data = data)
