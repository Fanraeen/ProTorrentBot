from requests import get
from requests.exceptions import ProxyError

def read_proxy():
    proxy_file = open('proxy.txt', 'r')
    for line in proxy_file.readlines():
        proxy_line = 'socks5://{}'.format(line[:len(line)])
        proxies = {
            'http': proxy_line,
            'https': proxy_line
        }
        try:
            get('https://rutracker.org', proxies=proxies)
        except ProxyError:
            continue
        else:
            return proxies
    
    print('NONE PROXY')
    return None



