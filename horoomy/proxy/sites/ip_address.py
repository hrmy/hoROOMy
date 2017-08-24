from . import *


def parse(*args, **kwargs):
    html = requests.get('https://www.ip-adress.com/proxy-list').text
    soup = BS(html, 'lxml')
    table = soup.find('table', {'class': 'htable proxylist'})
    raw_proxies = [row.find('td').text for row in table.find_all('tr')[1:-1]]
    proxies = [i.strip().replace(' ', '') for i in raw_proxies]

    for proxy in proxies:
        proxy = test_proxy(fullstrip(proxy))
        if not proxy: continue
        yield proxy