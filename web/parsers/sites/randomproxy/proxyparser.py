import requests
from bs4 import BeautifulSoup

from log import log, clearlog


timeout = 15
stats = {}


def clear_proxy(type = 'all'):
    if (type == 'all' or type == 'http'):
        with open('http_proxies.txt', 'w') as logfile:
            a = 1
        log('http-proxies cleared', head = 'proxyparser')
    if (type == 'all' or type == 'https'):
        with open('https_proxies.txt', 'w') as logfile:
            a = 1
        log('https-proxies cleared', head = 'proxyparser')


def add_proxy(proxy, type = 'http'):
    if (type == 'http'):
        with open('http_proxies.txt', 'a') as proxiesfile:
            proxiesfile.write(str(proxy) + '\n')

        log('added http-proxy: ' + proxy, head = 'proxyparser')
        stats['http'] += 1

    elif (type == 'https'):
        with open('https_proxies.txt', 'a') as proxiesfile:
            proxiesfile.write(str(proxy) + '\n')

        log('added https-proxy: ' + proxy, head = 'proxyparser')
        stats['https'] += 1



def parse_proxy():
    clear_proxy()

    url = 'https://www.ip-adress.com/proxy-list'
    stats['http'] = 0
    stats['https'] = 0

    log('Parsing started.', head='proxyparser')

    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')
    except Exception as exc:
        log(str(exc), True)

    try:
        proxy_table = soup.find('table', {'class': 'htable proxylist'})
        proxy_list = proxy_table.find_all('tr')
        proxy_list = proxy_list[1:-1]
    except Exception as exc:
        log(str(exc), True)

    log('Found %d proxies' % len(proxy_list), head = 'proxyparser')

    for number, proxy_element in enumerate(proxy_list):
        try:
            proxy = proxy_element.find('td')
            proxy = proxy.text.strip()
            log('Checking %d/%d proxy: ' % (number + 1, len(proxy_list)) + str(proxy), _print = True, head = 'proxyparser')
        except Exception as exc:
            log(str(exc), True)

        try:
            r = requests.get('http://sitespy.ru', proxies={'http': 'http://' + proxy}, timeout = timeout)
            log('http://sitespy.ru: ' + str(r.status_code), _print = True, head = 'proxyparser')
            if (r.status_code == 200):
                add_proxy(proxy, 'http')
        except Exception as exc:
            log('http://sitespy.ru: ' + str(exc), _print = True, head = 'proxyparser')

        try:
            r = requests.get('https://pythonworld.ru', proxies={'https': 'https://' + proxy}, timeout = timeout)
            log('https://pythonworld.ru: ' + str(r.status_code), _print = True, head = 'proxyparser')
            if (r.status_code == 200):
                add_proxy(proxy, 'https')
        except Exception as exc:
            log('https://pythonworld.ru: ' + str(exc), _print = True, head = 'proxyparser')

        log('', _print = True)

    log('Parsing finished. Found %d valid http-proxies and %d valid https-proxies.' % (stats['http'], stats['https']), _print = True, head = 'proxyparser')
    log('', _print = True)


parse_proxy()