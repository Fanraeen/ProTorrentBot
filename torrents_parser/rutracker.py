from requests import Session
from bs4 import BeautifulSoup
from proxy import read_proxy

from login_data import RUTRACKER, HEADERS


class RuTracker:
    def __init__(self):
        self.session = Session()

    def login(self):
        proxies = read_proxy()
        print('rurtracker.org/login.php')
        server_login = self.session.post(url='http://rutracker.org/forum/login.php',
                                         data={'login_username': RUTRACKER['username'],
                                               'login_password': RUTRACKER['password'],
                                               'redirect': 'index.php',
                                               'login': '(unable to decode value)'},
                                         proxies=proxies,
                                         headers=HEADERS)
        print('IM HERE')
        print(self.session.cookies)
        soup = BeautifulSoup(server_login.content, 'lxml')
        with open('login.html', 'w') as file:
            file.write(soup.prettify())

        home_page = self.session.get(
            url='https://rutracker.org', proxies=proxies, headers=HEADERS)

        with open('index.html', 'w') as file:
            soup = BeautifulSoup(home_page.content, 'lxml')
            file.write(soup.prettify())


rutracker_user = RuTracker()
rutracker_user.login()
