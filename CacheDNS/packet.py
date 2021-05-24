from struct import unpack, pack
from io import BytesIO


RECORD_TYPES = {1: 'A', 2: 'NS', 12: 'PTR', 28: 'AAAA'}
RECORD_TYPES_TO_INT = {'A': 1, 'NS': 2, 'PTR': 12, 'AAAA': 28}


class Header:
    def __init__(self, data: BytesIO):
        self._data = data.read(12)
        (self.id, self.option, self.qdcount, self.ancount, self.nscount,
         self.arcount) = unpack('!H H H H H H', self._data)

    def set_response_bits(self, ancount, nscount, arcount):
        option = self.option | 16384
        self._data = (pack('! H H H H H H', self.id,
                           option, self.qdcount, ancount, nscount, arcount))

    def __bytes__(self) -> bytes:
        return self._data


class Name:
    def __init__(self, bytestream: BytesIO = None, all_data: bytes = b'',
                 name=None):
        if bytestream is not None:
            self.all_data = all_data
            self._bytestream = bytestream
            self.value = self._parse(self._bytestream, self.all_data)
        else:
            self.value = name

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

    def __bytes__(self) -> bytes:
        result = b''
        for fragment in self.value.split('.'):
            result += pack('!B', len(fragment))
            result += bytes(fragment, 'ASCII')
        result += pack("!B", 0)
        return result

    def get_ip(self) -> bytes:
        result = b''
        for fragment in self.value.split('.'):
            result += pack("!B", int(fragment))
        return result


class Question:
    def __init__(self, name: Name, data: BytesIO):
        self.name = name
        self._data = data
        self.q_type, self.q_class = unpack('!H H', data.read(4))

    def __bytes__(self) -> bytes:
        return bytes(self.name) + pack('!H H', self.q_type, self.q_class)


class Record:
    def __init__(self, name: Name, data: BytesIO):
        self.name = name
        self._data = data
        (self.ans_type, self.ans_class, self.ttl,
         self.rec_len, self.rec_data) = self._parse()

    def _parse(self) -> tuple[str, int, int, int, Name]:
        (ans_type, ans_class, ttl, rec_len) = unpack('!H H I H',
                                                     self._data.read(10))
        rec_data = self._parse_address(rec_len, get_str_type(ans_type))
        return (get_str_type(ans_type), ans_class,
                int(ttl), int(rec_len), rec_data)

    @property
    def value(self) -> str:
        return self.rec_data.value

    def _parse_address(self, length: int, ans_type: str) -> Name:
        if ans_type == 'A':
            name = '.'.join(['{}'.format(self._data.read(1)[0])
                             for _ in range(length)])
            return Name(name=name)
        elif ans_type == 'NS':
            return Name(self._data, self.name.all_data)
        else:
            return Name(name='')

    def __bytes__(self) -> bytes:
        result = bytes(self.name) + pack('!H H I H',
                                         get_int_type(self.ans_type),
                                         self.ans_class, self.ttl,
                                         self.rec_len)
        if self.ans_type == 'A':
            result += self.rec_data.get_ip()
        else:
            result += bytes(self.rec_data)
        return result


class Packet:
    def __init__(self, data: bytes):
        self._data = data
        self._bytestream = BytesIO(data)
        self.header = Header(self._bytestream)
        self.questions = self._parse_questions(self.header.qdcount)
        self.ans_records = self._parse_records(self.header.ancount)
        self.auth_records = self._parse_records(self.header.nscount)
        self.add_records = self._parse_records(self.header.arcount)

    def _parse_questions(self, count: int) -> list[Question]:
        return [Question(Name(self._bytestream, self._data),
                         self._bytestream) for _ in range(count)]

    def _parse_records(self, count: int) -> list[Record]:
        return [Record(Name(self._bytestream, self._data),
                       self._bytestream) for _ in range(count)]

    def __bytes__(self) -> bytes:
        result = bytes(self.header)
        for question in self.questions:
            result += bytes(question)
        for answer in self.ans_records:
            result += bytes(answer)
        return result


def get_str_type(ans_type: int) -> str:
    if ans_type in RECORD_TYPES.keys():
        return RECORD_TYPES[ans_type]
    return 'undefined'  # TODO


def get_int_type(ans_type: str) -> int:
    if ans_type in RECORD_TYPES_TO_INT.keys():
        return RECORD_TYPES_TO_INT[ans_type]
    return 0    # TODO
