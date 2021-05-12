import socket

from packet import Packet
from config import Config
from cache import Cache
# вот, гнида, получи свою четверку


class RequestHandler:
    def __init__(self, config: Config, cache: Cache):
        self._cache = cache
        self._config = config

    def handle_query(self, query_bytes: bytes) -> bytes:
        query_msg = Packet(query_bytes)
        question = query_msg.questions[0]
        print(f'Client request for {question.name.value}')
        if question.name.value in self._cache:
            return self._cache[question.name.value]
        dns_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_client.sendto(query_bytes, self._config.forwarder_address)
        raw_data = dns_client.recv(self._config.buffer_size)
        packet = Packet(raw_data)
        self._cache.add(question.name.value, packet)
        print(f'DNS answer for {question.name.value}:',
              packet.ans_records[0].ip)
        return raw_data
