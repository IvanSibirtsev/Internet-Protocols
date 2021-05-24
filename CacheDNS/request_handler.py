import socket

from packet import Packet, Record, get_str_type
from config import Config
from cache import Cache


class RequestHandler:
    def __init__(self, config: Config, cache: Cache):
        self._cache = cache
        self._config = config

    def handle_query(self, query_bytes: bytes) -> bytes:
        query_msg = Packet(query_bytes)
        question = query_msg.questions[0]
        print(f'Client request for {question.name.value}')
        tup = (question.name.value, get_str_type(question.q_type))
        if tup in self._cache:
            print('\t', question.name.value, "found in cache")
            answers, ans_type = self._cache[tup]
            print('\t', f'DNS answer for {question.name.value}:',
                  answers.value)

            response = self.make_response(query_msg, answers, ans_type)
        else:
            print('\t', question.name.value, 'couldnt find in cache')
            dns_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dns_client.sendto(query_bytes, self._config.forwarder_address)
            raw_data = dns_client.recv(self._config.buffer_size)
            packet = Packet(raw_data)
            print('\t', f'DNS answer for {question.name.value}:',
                  packet.ans_records[0].value)

            for record in packet.ans_records:
                self._cache.add((record.name.value, record.ans_type), record, 'ans')
            for record in packet.auth_records:
                self._cache.add((record.name.value, record.ans_type), record, 'auth')
            for record in packet.add_records:
                self._cache.add((record.name.value, record.ans_type), record, 'add')

            response = raw_data

        return response

    def make_response(self, query_packet: Packet,
                      answer: Record, ans_type: str) -> bytes:
        ans = auth = add = 0
        if ans_type == 'ans':
            ans = 1
        if ans_type == 'auth':
            auth = 1
        if ans_type == 'add':
            add = 1
        query_packet.header.set_response_bits(ans, auth, add)
        query_packet.ans_records = [answer]
        return bytes(query_packet)
