from decimal import Decimal
from time import time
import pickle

from packet import Record


class Cache:
    def __init__(self, cache=None, cache_ttl=None):
        self._cache = {}
        self._time = {}
        if cache:
            self._cache = cache
            self._time = cache_ttl

    def add(self, tup: tuple[str, str], record: Record):
        self._cache[tup] = record
        print(tup[0])
        self._time[tup] = record.ttl + time()

    def __contains__(self, tup: tuple[str, str]) -> bool:
        self._clean()
        return tup in self._cache.keys()

    def __getitem__(self, tup: tuple[str, str]) -> Record:
        if tup in self:
            print(f'This name - {tup[0]} was taken from cache.')
            return self._cache[tup]
        else:
            return b''  # TODO

    def _clean(self):
        names = list(self._cache.keys())
        for record in names:
            if Decimal(self._time[record]) < Decimal(time()):
                self._cache.pop(record)
                self._time.pop(record)

    @staticmethod
    def from_dump(filename: str) -> 'Cache':
        try:
            with open(filename, 'rb') as dump:
                cache = pickle.load(dump)
            print('Get saved cache.')
            return cache
        except EOFError:
            print('No cache.')
            return Cache()

    def dump_to_file(self, filename: str):
        with open(filename, 'wb') as dump:
            pickle.dump(self, dump)
