from struct import unpack
from io import BytesIO
import socket


class Header:
    def __init__(self, data: BytesIO):
        (self.id, self.option, self.qdcount, self.ancount, self.nscount,
         self.arcount) = unpack('!HHHHHH', data.read(12))


class Name:
    def __init__(self, bytestream: BytesIO, all_data: bytes):
        self._all_data = all_data
        self._bytestream = bytestream
        self.value = self._parse(self._bytestream, self._all_data)

    def _parse(self, data: BytesIO, all_data: bytes) -> str:
        length = data.read(1)[0]
        if length == 0:
            return ''
        if length < 192:
            name = f"{data.read(length).decode('ASCII')}."
            rec_name = self._parse(data, all_data)
            return (name + rec_name).rstrip('.')
        else:
            second_part = data.read(1)[0]
            offset = (length - 192) * 256 + second_part
            return self._parse(BytesIO(all_data[offset:]), all_data)


class Question:
    def __init__(self, name: Name, data: BytesIO):
        self.name = name
        self._data = data
        self.q_type, self.q_class = unpack('!HH', data.read(4))


class Record:
    _RECORD_TYPES = {1: 'A', 2: 'NS', 12: 'PTR', 28: 'AAAA'}

    def __init__(self, name: Name, data: BytesIO):
        self.name = name
        self._data = data
        (self.ans_type, self.ans_class, self.ttl,
         self.rec_len, self.rec_data) = self._parse()

    def _parse(self) -> tuple[str, int, int, int, bytes]:
        (ans_type, ans_class, ttl, rec_len) = unpack('!HHIH',
                                                     self._data.read(10))
        rec_data = self._data.read(rec_len)

        return (self.get_type(ans_type), ans_class,
                int(ttl), int(rec_len), rec_data)

    def get_type(self, ans_type: int) -> str:
        if ans_type in self._RECORD_TYPES.keys():
            return self._RECORD_TYPES[ans_type]
        return 'undefined'

    @property
    def ip(self) -> str:
        return socket.inet_ntoa(self.rec_data)


class Packet:
    def __init__(self, data: bytes):
        self._data = data
        self._bytestream = BytesIO(data)
        self._header = Header(self._bytestream)
        self.questions = self._parse_questions(self._header.qdcount)
        self.ans_records = self._parse_records(self._header.ancount)
        self._auth_records = self._parse_records(self._header.nscount)
        self._add_records = self._parse_records(self._header.arcount)

    def _parse_questions(self, count: int) -> list[Question]:
        return [Question(Name(self._bytestream, self._data),
                         self._bytestream) for _ in range(count)]

    def _parse_records(self, count: int) -> list[Record]:
        return [Record(Name(self._bytestream, self._data),
                       self._bytestream) for _ in range(count)]

    @property
    def raw_data(self) -> bytes:
        return self._data
