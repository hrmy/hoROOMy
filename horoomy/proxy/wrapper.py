from .models import Proxy, UserAgent
from .settings import *
import requests

PROXIES = {
    'enabled': [],
    'disabled': []
}
USER_AGENTS = {
    'enabled': [],
    'disabled': []
}


def reset_proxies():
    PROXIES['enabled'] = []
    PROXIES['disabled'] = []
    for i in Proxy.objects.all():
        i.requests = 0
        PROXIES['enabled'].append(i)


def reset_user_agents():
    USER_AGENTS['enabled'] = []
    USER_AGENTS['disabled'] = []
    for i in UserAgent.objects.all():
        i.requests = 0
        USER_AGENTS['enabled'].append(i)


def get_proxy(type):
    if not PROXIES['enabled']: reset_proxies()
    for i, x in enumerate(PROXIES['enabled']):
        if x.type == type or x.type == Proxy.TYPES.BOTH:
            index = i
            proxy = x
            break
    else:
        reset_proxies()
        return get_proxy(type)
    proxy.requests += 1
    if proxy.requests == PROXY_REQUESTS:
        PROXIES['enabled'].pop(index)
        PROXIES['disabled'].append(proxy)
    proxies = {
        'http': proxy.address,
        'https': proxy.address
    }
    return proxies


def get_user_agent():
    if not USER_AGENTS['enabled']: reset_user_agents()
    user_agent = USER_AGENTS['enabled'][0]
    user_agent.requests += 1
    if user_agent.requests == USER_AGENT_REQUESTS:
        USER_AGENTS['enabled'].pop(0)
        USER_AGENTS['disabled'].append(user_agent)
    return {'User-Agent': user_agent.value}


def request(method, url, **kwargs):
    schema = url.split(':')[0].upper()
    type = getattr(Proxy.TYPES, schema)
    proxies = get_proxy(type)
    headers = get_user_agent()
    try:
        if method.upper() == 'GET':
            r = requests.get(url, proxies=proxies, headers=headers, timeout=PROXY_TIMEOUT, **kwargs)
        elif method.upper() == 'POST':
            r = requests.post(url, proxies=proxies, headers=headers, timeout=PROXY_TIMEOUT, **kwargs)
        else:
            return None
    except:
        print('PROXY FAILED')
        return request(method, url, **kwargs)
    return r


get = lambda url, **kwargs: request('get', url, **kwargs)
post = lambda url, **kwargs: request('post', url, **kwargs)