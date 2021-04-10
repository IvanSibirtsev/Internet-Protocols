from concurrent.futures import ThreadPoolExecutor
from typing import NoReturn
from struct import pack
import socket

from args import Args


PACKET = b'\x13' + b'\x00' * 39 + b'\x6f\x89\xe9\x1a\xb6\xd5\x3b\xd3'


class DNS:
    @staticmethod
    def is_dns(packet: bytes) -> bool:
        transaction_id = PACKET[:2]
        return transaction_id in packet


class SNTP:
    @staticmethod
    def is_sntp(packet: bytes) -> bool:
        transmit_timestamp = PACKET[-8:]
        origin_timestamp = packet[24:32]
        is_packet_from_server = 7 & packet[0] == 4
        return len(packet) >= 48 and \
            is_packet_from_server and \
            origin_timestamp == transmit_timestamp


class POP3:
    @staticmethod
    def is_pop3(packet: bytes) -> bool:
        return packet.startswith(b'+')


class HTTP:
    @staticmethod
    def is_html(packet: bytes) -> bool:
        return b'HTTP' in packet


class SMTP:
    @staticmethod
    def is_smtp(packet: bytes) -> bool:
        return packet[:3].isdigit()


class Scanner:
    _PROTOCOL_DEFINER = {
        'SMTP': lambda packet: SMTP.is_smtp(packet),
        'DNS': lambda packet: DNS.is_dns(packet),
        'POP3': lambda packet: POP3.is_pop3(packet),
        'HTTP': lambda packet: HTTP.is_html(packet),
        'SNTP': lambda packet: SNTP.is_sntp(packet)
    }

    def __init__(self, host: str):
        self._host = host

    def tcp_port(self, port: int) -> str:
        socket.setdefaulttimeout(0.5)
        result = ''
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as scanner:
            try:
                scanner.connect((self._host, port))
                result = f'TCP {port} - Open.'
            except (socket.timeout, TimeoutError, OSError):
                pass
            try:
                scanner.send(pack('!H', len(PACKET)) + PACKET)
                data = scanner.recv(1024)
                result += f' {self._check(data)}'
            except socket.error:
                pass
        return result

    def udp_port(self, port: int) -> str:
        socket.setdefaulttimeout(3)
        result = ''
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as scanner:
            try:
                scanner.sendto(PACKET, (self._host, port))
                data, _ = scanner.recvfrom(1024)
                result = f'UDP {port} - Open. {self._check(data)}'
            except socket.error:
                pass
        return result

    def _check(self, data: bytes) -> str:
        for protocol, checker in self._PROTOCOL_DEFINER.items():
            if checker(data):
                return protocol
        return ''


def main(host: str, start: int, end: int) -> NoReturn:
    scanner = Scanner(host)
    with ThreadPoolExecutor(max_workers=300) as pool:
        for port in range(start, end + 1):
            pool.submit(execute, scanner, port)


def execute(scanner: Scanner, port: int) -> NoReturn:
    show(scanner.tcp_port(port))
    show(scanner.udp_port(port))


def show(result: str) -> NoReturn:
    if result:
        print(result)


if __name__ == "__main__":
    args = Args()
    main(args.host, args.start, args.end)
