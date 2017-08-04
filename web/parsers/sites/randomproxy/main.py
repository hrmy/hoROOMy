import requests
from random import choice

from randomproxy.log import log


def get_proxy():

    with open('randomproxy/http_proxies.txt', 'r') as f:
        http_proxies = f.read().split('\n')
    with open('randomproxy/https_proxies.txt', 'r') as f:
        https_proxies = f.read().split('\n')

    proxy = {'http': 'http://' + choice(http_proxies),
             'https': 'https://' + choice(https_proxies)}
    return proxy


def get_useragent():

    with open('randomproxy/headers.txt', 'r') as f:
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
    log('GET ' + url, _print=True, head='main.get')

    times = 0
    maxtimes = 7
    timeout = 15

    while times <= maxtimes:
        times += 1

        try:
            proxy = get_proxy()
            useragent = get_useragent()
        except Exception as exc:
            log(str(exc), _print=True, head='main.get')
            continue

        log('proxy = ' + str(proxy), _print=True, head='main.get')
        log('useragent = ' + str(useragent), _print=True, head='main.get')

        try:
            r = make_request(url, rtype=rtype, data=data, headers=useragent, proxies=proxy, timeout=timeout)
            if (r.status_code == 200):
                log('success', _print=True, head='main.get')
                return r
            else:
                log('Unsuccess. Request is done, but status code is %d' % r.status_code, head='main.get')
        except Exception as exc:
            log(str(exc), _print=True, head='main.get')
            log('unsuccess', head='main.get')

        log('', _print=True)

    log('proxie did not work %d times, returning request made only with headers' % maxtimes, head='main.get')

    try:
        useragent = get_useragent()
        r = make_request(url, rtype=rtype, data=data, headers=useragent)
        return r
    except Exception as exc:
        log(str(exc), head='main.get')
        log('request caused an error, returning None', head='main.get')
        return exc


def get(url):
    return getpost(url, rtype = 'get')


def post(url, data):
    return getpost(url, rtype = 'post', data = data)
