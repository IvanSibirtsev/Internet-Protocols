import struct
from timestamp import Timestamp


class SNTP:
    """https://tools.ietf.org/html/rfc4330"""
    _HEADER_FORMAT = '> B B B B I I 4s Q Q Q Q'
    _LEAP_INDICATOR = 0  # no warning
    _VERSION_NUMBER = 4  # NTP/SNTP version number
    _MODE = 4  # server
    _STRATUM = 1  # synchronized
    _FIRST_OCTET = _LEAP_INDICATOR << 6 | _VERSION_NUMBER << 3 | _MODE
    CLIENT_REQUEST = '\x1b' + 47 * '\0'

    def __init__(self, time_delta: float = 0):
        self._received_time = Timestamp.time_with_delta(0)
        self._time_delta = time_delta
        self._transmit_time = 0

    def analise_packet(self, received_packet: bytes) -> None:
        self._transmit_time = self._get_transmit_time(received_packet)

    def _get_transmit_time(self, received_packet: bytes) -> int:
        return struct.unpack(self._HEADER_FORMAT, received_packet)[10]

    def get_server_packet(self) -> bytes:
        return struct.pack(self._HEADER_FORMAT, self._FIRST_OCTET,
                           self._STRATUM, 0, 0, 0, 0, b'', 0,
                           self._transmit_time, self._received_time,
                           Timestamp.time_with_delta(self._time_delta))

    @staticmethod
    def time_from_client_answer(data) -> int:
        return struct.unpack('!12I', data)[10]
