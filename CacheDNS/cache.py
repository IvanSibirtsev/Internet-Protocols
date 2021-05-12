from typing import NoReturn
from decimal import Decimal
from time import time
import pickle

from packet import Packet


class Cache:
    def __init__(self, cache: dict[str, bytes] = None,
                 cache_ttl: dict[str, float] = None):
        self._cache = {}
        self._time = {}
        if cache:
            self._cache = cache
            self._time = cache_ttl

    def add(self, name: str, packet: Packet) -> NoReturn:
        self._cache[name] = packet.raw_data
        self._time[name] = packet.ans_records[0].ttl + time()

    def __contains__(self, ip: str) -> bool:
        self._clean()
        return ip in self._cache

    def __getitem__(self, name: str) -> bytes:
        if name in self:
            print(f'This name - {name} was taken from cache.')
            return self._cache[name]
        else:
            return b''

    def _clean(self) -> NoReturn:
        names = list(self._cache.keys())
        for record in names:
            if Decimal(self._time[record]) < Decimal(time()):
                self._cache.pop(record)
                self._time.pop(record)

    @staticmethod
    def from_dump(filename: str) -> 'Cache':
        with open(filename, 'rb') as dump:
            cache = pickle.load(dump)
        if isinstance(cache, Cache):
            print('Get saved cache.')
            return cache
        else:
            print('No cache.')
            return Cache()

    def dump_to_file(self, filename: str) -> NoReturn:
        with open(filename, 'wb') as dump:
            pickle.dump(self, dump)
