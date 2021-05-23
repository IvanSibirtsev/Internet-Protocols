import re
import subprocess
from json import loads
from typing import Optional, IO
from urllib import request
import locale
import argparse


ip_regex = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

EN_DICT = {
    'invalid input': 'Unable to resolve',
    'tracing': 'Tracing route',
    'host unreachable': 'Destination Host Unreachable',
    'trace complete': 'Trace complete',
    'max hops': 'over a maximum of'
}

RU_DICT = {
    'invalid input': 'Не удается разрешить системное имя узла',
    'tracing': 'Трассировка маршрута',
    'host unreachable': 'Заданный узел недоступен.',
    'trace complete': 'Трассировка завершена',
    'max hops': 'с максимальным числом прыжков'
}

SYSTEM_MESSAGES = {
    'ru_RU': RU_DICT,
    'en_EN': EN_DICT
}


class ASResponse:
    def __init__(self, json: dict):
        self._json = json
        self._parse()

    def _parse(self):
        self.ip = self._json.get('ip') or '--'
        self.city = self._json.get('city') or '--'
        self.hostname = self._json.get('hostname') or '--'
        self.country = self._json.get('country') or '--'
        if org := self._json.get('org'):
            self.AS, self.provider = org.split()[0], ' '.join(org.split()[1:])
        else:
            self.AS, self.provider = '--', '--'


class Output:
    _IP_LEN = 15
    _AS_LEN = 6
    _COUNTRY_CITY_LEN = 18

    def __init__(self):
        self._number = 1

    def print(self, ip: str, AS: str, country: str, city: str, provider: str):
        if self._number == 1:
            self._print_header()
        string = f'{self._number}' + ' ' * (3 - len(str(self._number)))
        string += ip + self._spaces(self._IP_LEN, len(ip))
        string += AS + self._spaces(self._AS_LEN, len(AS))
        country_city = f'{country}/{city}'
        string += country_city + self._spaces(self._COUNTRY_CITY_LEN,
                                              len(country_city))
        string += provider
        self._number += 1
        print(string)

    @staticmethod
    def _print_header():
        print('№  IP' + ' ' * 16 + 'AS' + ' ' * 7 +
              'Country/City' + ' ' * 9 + 'Provider')

    @staticmethod
    def _spaces(expected: int, actual: int) -> str:
        return ' ' * (3 + (expected - actual))


def get_as_number_by_ip(ip) -> ASResponse:
    inf = loads(request.urlopen('https://ipinfo.io/' + ip + '/json').read())
    return ASResponse(inf)


def get_route(address: str, os_lang: dict[str, str]):
    tracert = subprocess.Popen(['tracert', address], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    get_as = False
    output = Output()
    for line in iter(tracert.stdout.readline, ""):
        line = line.decode(encoding='cp866')
        if line.find(os_lang['invalid input']) != -1:
            print(line)
            break
        elif line.find(os_lang['tracing']) != -1:
            print(line, end='')
            end = ip_regex.findall(line)[0]
        elif line.find(os_lang['max hops']) != -1:
            get_as = True
        elif line.find(os_lang['host unreachable']) != -1:
            print(line.removeprefix(' '))
            break
        elif line.find(os_lang['trace complete']) != -1:
            print(line)
            break

        try:
            ip = ip_regex.findall(line)[0]
        except IndexError:
            continue

        if get_as:
            response = get_as_number_by_ip(ip)
            output.print(response.ip, response.AS,
                         response.country, response.city, response.provider)
            if ip == end:
                print('Трассировка завершена.')
                break


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Autonomous Systems tracert')
    parser.add_argument('address', type=str,
                        help='Destination to which utility traces route.')
    return parser.parse_args()


if __name__ == '__main__':
    site = parse_args()
    lang = locale.getdefaultlocale()[0]
    if not SYSTEM_MESSAGES.get(lang):
        print('please enter your cmd lang [ru, en]')
        lang = 'ru_RU' if 'ru' in input() else 'en_EN'
    get_route(site.address, SYSTEM_MESSAGES[lang])
