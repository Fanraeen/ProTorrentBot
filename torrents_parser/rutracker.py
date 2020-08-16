from requests import Session
from bs4 import BeautifulSoup
from torrents_parser.proxy import read_proxy
import pickle

from torrents_parser.exceptions import LoginError
from torrents_parser.login_data import *


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
        self.auth = False

    def login(self):
        if self.auth:
            return self.session

        try:
            with open('torrents_parser/sessions/rutracker', 'rb') as f:
                self.session.cookies.update(pickle.load(f))
        except FileNotFoundError:
            pass
        else:
            self.auth = True
            return self.session

        proxies = read_proxy()
        server_login = self.session.post(url='http://rutracker.org/forum/login.php',
                                         data=RUTRACKER_LOGIN,
                                         proxies=proxies,
                                         headers=HEADERS)
        if len(self.session.cookies) == 0:
            auth_status = login_status(server_login)
            if auth_status == 'need captcha':
                captcha_data = get_captcha(server_login)
                RUTRACKER_LOGIN['cap_sid'] = captcha_data['cap_sid']
                RUTRACKER_LOGIN[captcha_data['cap_code']
                                ] = captcha_data['captcha_code']
                server_login = self.session.post(url='https://rutracker.org/forum/login.php',
                                                 data=RUTRACKER_LOGIN,
                                                 proxies=proxies,
                                                 headers=HEADERS)
            elif auth_status == 'wrong login or password':
                raise LoginError('wrong login or password')
        else:
            self.auth = True
            with open('sessions/rutracker', 'wb') as f:
                pickle.dump(self.session.cookies, f)

    def search(self, q_str: str):
        rutracker_data = []
        if not self.auth:
            raise LoginError('Please user login() before')
        proxies = read_proxy(check=False)
        search_data = self.session.get(url='https://rutracker.org/forum/tracker.php',
                                       params={'nm': q_str},
                                       proxies=proxies,
                                       headers=HEADERS)
        soup = BeautifulSoup(search_data.content, 'lxml')
        search_result = soup.find('div', {'id': 'search-results'})
        table_body = search_result.find('tbody')
        table_elems = table_body.find_all('tr')

        for elem in table_elems:
            if len(elem.find_all(attrs={'title': 'проверено'})) == 0:
                check_status = False
            else:
                check_status = True

            elem_info = elem.find('a', {'class': 'tLink'})
            try:
                link = elem_info.attrs['href']
            except AttributeError:
                continue

            name = elem_info.get_text(strip=True)
            try:
                size = elem.find('a', {'class': 'dl-stub'}).get_text(strip=True)
            except AttributeError:
                size = 'None :()'
            try:
                seedmed = elem.find('b', {'class': 'seedmed'}).contents[0]
            except AttributeError:
                seedmed = '0'

            rutracker_data.append({
                'check_status': check_status,
                'link': link,
                'name': name,
                'size': size.replace(u'\xa0', u' ')[:-2],
                'seeders': seedmed
            })

        return rutracker_data

    def torrent_details(self, torrent_id: int, link=None):
        if not self.auth:
            raise LoginError('For see torrent details - login()')
        proxies = read_proxy(check=False)
        torrent_page = self.session.get(url='https://rutracker.org/forum/viewtopic.php?t={}'.format(torrent_id),
                                        proxies=proxies,
                                        headers=HEADERS)
        soup = BeautifulSoup(torrent_page.content, 'lxml')
        seed = soup.find('span', {'class': 'seed'}).find('b').string
        post_wrap = soup.find('div', {'class': 'post_wrap'})
        
        with open('index.html', 'w') as f:
            f.write(soup.prettify())

        image = post_wrap.find('var', {'class': 'postImg'}).attrs['title']
        torrent_file_url = post_wrap.find('a', {'class': 'dl-stub dl-link dl-topic'}).attrs['href']
        magnet_link = post_wrap.find('a', {'class': 'med magnet-link'}).attrs['href']

        torrent_details_data = {}
        torrent_details_data['seed'] = seed
        torrent_details_data['.torrent'] = 'rutracker.org/forum/' + torrent_file_url
        torrent_details_data['magnet_link'] = 'https://rutracker.org/forum/' + magnet_link
        if image[-3:] in ['png', 'jpg']:
            pass
        else:
            image = None

        description = soup.title.get_text(strip=True) + '\n'
        for span in post_wrap.find_all('span', class_='post-b'):
            if span.next_sibling is None:
                continue
            next_elem = span.next_sibling
            if next_elem == ': ':
                next_elem = next_elem.next_element
                
                if next_elem.name == 'br':
                    next_elem = next_elem.next_element

                if next_elem.name is not None:
                    next_elem = next_elem.string
            
            if len(next_elem) <= 3:
                continue

            description+=('**{}** {}\n'.format(
                span.get_text(strip=True),
                next_elem
            ))

            torrent_details_data['description'] = description
            torrent_details_data['image'] = image 

        return torrent_details_data

