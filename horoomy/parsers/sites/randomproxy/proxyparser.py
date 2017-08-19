import requests
from bs4 import BeautifulSoup
from celery import shared_task


timeout = 15
stats = {}


def clear_proxy(type = 'all'):
    if (type == 'all' or type == 'http'):
        with open('http_proxies.txt', 'w') as logfile:
            a = 1
        print('http-proxies cleared')
    if (type == 'all' or type == 'https'):
        with open('https_proxies.txt', 'w') as logfile:
            a = 1
        print('https-proxies cleared')


def add_proxy(proxy, type = 'http'):
    if (type == 'http'):
        with open('http_proxies.txt', 'a') as proxiesfile:
            proxiesfile.write(str(proxy) + '\n')

        print('added http-proxy: ' + proxy)
        stats['http'] += 1

    elif (type == 'https'):
        with open('https_proxies.txt', 'a') as proxiesfile:
            proxiesfile.write(str(proxy) + '\n')

        print('added https-proxy: ' + proxy)
        stats['https'] += 1


@shared_task(name='parsers.parse_proxies')
def parse_proxy():
    clear_proxy()

    url = 'https://www.ip-adress.com/proxy-list'
    stats['http'] = 0
    stats['https'] = 0

    print('Parsing started.')

    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')
    except Exception as exc:
        print(str(exc))

    try:
        proxy_table = soup.find('table', {'class': 'htable proxylist'})
        proxy_list = proxy_table.find_all('tr')
        proxy_list = proxy_list[1:-1]
    except Exception as exc:
        print(str(exc))

    print('Found %d proxies' % len(proxy_list))

    for number, proxy_element in enumerate(proxy_list):
        try:
            proxy = proxy_element.find('td')
            proxy = proxy.text.strip()
            print('Checking %d/%d proxy: ' % (number + 1, len(proxy_list)) + str(proxy))
        except Exception as exc:
            print(str(exc))

        try:
            r = requests.get('http://sitespy.ru', proxies={'http': 'http://' + proxy}, timeout = timeout)
            print('http://sitespy.ru: ' + str(r.status_code))
            if (r.status_code == 200):
                add_proxy(proxy, 'http')
        except Exception as exc:
            print('http://sitespy.ru: ' + str(exc))

        try:
            r = requests.get('https://pythonworld.ru', proxies={'https': 'https://' + proxy}, timeout = timeout)
            print('https://pythonworld.ru: ' + str(r.status_code))
            if (r.status_code == 200):
                add_proxy(proxy, 'https')
        except Exception as exc:
            print('https://pythonworld.ru: ' + str(exc))

        #log('', _print = True)

    print('Parsing finished. Found %d valid http-proxies and %d valid https-proxies.' % (stats['http'], stats['https']))
