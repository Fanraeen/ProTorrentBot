from requests import get
from requests.exceptions import ProxyError

def read_proxy(check=True):
    proxy_file = open('torrents_parser/proxy.txt', 'r')
    for line in proxy_file.readlines():
        proxy_line = 'socks5://{}'.format(line[:len(line)])
        proxies = {
            'http': proxy_line,
            'https': proxy_line
        }
        if check:
            try:
                get('https://rutracker.org', proxies=proxies)
            except ProxyError:
                continue
            else:
                return proxies
        else:
            return proxies
    
    print('NONE PROXY')
    return None



