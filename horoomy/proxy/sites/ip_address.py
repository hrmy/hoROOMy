from . import *


def test(url, proxy):
    proxies = {'http': proxy, 'https': proxy}
    try:
        start = time()
        r = requests.get(url, timeout=PROXY_TIMEOUT, proxies=proxies)
        delta = time() - start
        if r.status_code != 200: return False
    except:
        return False
    return delta


def parse(*args, **kwargs):
    html = requests.get('https://www.ip-adress.com/proxy-list').text
    soup = BS(html, 'lxml')
    table = soup.find('table', {'class': 'htable proxylist'})
    raw_proxies = [row.find('td').text for row in table.find_all('tr')[1:-1]]
    proxies = [i.strip().replace(' ', '') for i in raw_proxies]

    for proxy in proxies:
        http = test(HTTP_URL, proxy)
        https = test(HTTPS_URL, proxy)
        if not http and not https: continue
        proxy = {'address': proxy}
        if http and https:
            proxy['type'] = Proxy.TYPES.BOTH
            speed = 2 / (http + https)
        else:
            proxy['type'] = Proxy.TYPES.HTTP if http else Proxy.TYPES.HTTPS
            speed = 1 / (http or https)
        proxy['speed'] = speed * 1000
        yield proxy