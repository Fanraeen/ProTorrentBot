from torrents_parser.rutracker import RuTracker


rutracker_user = RuTracker()
rutracker_user.login()

def details_build_text(torrent_id: int):
    details_data = rutracker_user.torrent_details(torrent_id=torrent_id)
    message = '''{description}
🤝 <b>{seed} сидов</b>
    '''.format(
        description=details_data['description'],
        seed=details_data['seed']
    )

    return message


def torrent_file_path(torrent_id: int):
    path_to_file = rutracker_user.download_file(torrent_id=torrent_id)
    return path_to_file


def search_build_text(q_str: str, count=10):
    message = ''
    result_count = 0

    for elem in rutracker_user.search(q_str=q_str)[:10]:
        if result_count >= count:
            return message
        torrent_id = elem['link'].split('=')[1]
        if elem['check_status']:
            check = 'Проверено ✅'
        else:
            check = 'Не проверено 🚫'
        now_message = '''{name} 
{check}
💾 <b>{size}</b>
🤝 <b>{seed} сидов</b>
/torrent{torrent_id}
        '''.format(
            name=elem['name'],
            check=check,
            size=elem['size'],
            seed=elem['seeders'],
            torrent_id=torrent_id
        )

        message += now_message
        message += '\n'
        result_count += 1

    if message == '':
        message = 'Ничего не нашёл :((('

    return message


search_build_text('Тьма')
