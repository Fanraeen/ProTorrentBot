from requests import Session
from bs4 import BeautifulSoup
from proxy import read_proxy

from exceptions import LoginError
from login_data import RUTRACKER_LOGIN, HEADERS, RUTRACKER


def get_captcha(page):
    soup = BeautifulSoup(page.content, 'lxml')
    form = soup.find('table', {'class': 'forumline'})
    captcha_url = form.find('img').attrs['src']
    cap_sid = form.find('input', {'name': 'cap_sid'}).attrs['value']
    cap_code = form.find('input', {'class': 'reg-input'}).attrs['name']

    print(captcha_url)
    captcha_code = input('Please input captcha: ')
    return {'cap_sid': cap_sid, 'cap_code': cap_code, 'captcha_code': captcha_code}


def login_status(page):
    soup = BeautifulSoup(page.content, 'lxml')
    content = soup.find('div', {'id': 'main_content_wrap'})
    status_td = content.find('td', {'class': 'row1'})
    status_message = status_td.find('h4').contents[0]
    if 'код подтверждения' in status_message:
        return 'need captcha'
    elif 'неверный пароль' in status_message:
        return 'wrong login or password'
    else:
        return None


class RuTracker:
    def __init__(self):
        self.session = Session()

    def login(self):
        proxies = read_proxy()
        print('rutracker.org/forum/login.php')
        server_login = self.session.post(url='http://rutracker.org/forum/login.php',
                                         data=RUTRACKER_LOGIN,
                                         proxies=proxies,
                                         headers=HEADERS)
        print('IM HERE')
        if len(self.session.cookies) == 0:
            auth_status = login_status(server_login)
            if auth_status == 'need captcha':
                captcha_data = get_captcha(server_login)
                RUTRACKER_LOGIN['cap_sid'] = captcha_data['cap_sid']
                RUTRACKER_LOGIN[captcha_data['cap_code']] = captcha_data['captcha_code']
                print('SEND NEW DATA')
                print(RUTRACKER_LOGIN)
                server_login = self.session.post(url='http://rutracker.org/forum/login.php',
                                                 data=RUTRACKER_LOGIN,
                                                 proxies=proxies,
                                                 headers=HEADERS)
            elif auth_status == 'wrong login or password':
                print('wrong password or login')
        else:
            print('GOOD AUTH')

        soup = BeautifulSoup(server_login.content, 'lxml')
        with open('login.html', 'w') as file:
            file.write(soup.prettify())


rutracker_user = RuTracker()
rutracker_user.login()
