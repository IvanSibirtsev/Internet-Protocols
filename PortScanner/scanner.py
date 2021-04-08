import socket
from struct import pack
from port_scan import Args


class DNS:
    TRANSACTION_ID = b'\x08\xd3'
    _FLAGS = b'\x01\x00'  # recursion desired
    _QUESTION = b'\x00\x01'
    _ANSWER_AUTHORITY_ADDITIONAL = b'\x00\x00\x00\x00\x00\x00'
    _NAME = b'\x06\x67\x6f\x6c\x61\x6e\x67\x03\x6f\x72\x67\x00'  # golang.org
    _TYPE = b'\x00\x01'  # A (Host Address)
    CLASS = b'\x00\x01'

    @staticmethod
    def udp_query_packet() -> bytes:
        return DNS._question_packet()

    @staticmethod
    def tcp_query_packet() -> bytes:
        packet = DNS._question_packet()
        return pack('!H', len(packet)) + packet

    @staticmethod
    def _question_packet() -> bytes:
        return (DNS.TRANSACTION_ID + DNS._FLAGS + DNS._QUESTION +
                DNS._ANSWER_AUTHORITY_ADDITIONAL +
                DNS._NAME + DNS._TYPE + DNS.CLASS)

    @staticmethod
    def is_dns(packet: bytes) -> bool:
        return DNS.TRANSACTION_ID in packet


class SNTP:
    PACKET = '\x1b' + 47 * '\0'

    @staticmethod
    def is_sntp(packet: bytes) -> bool:
        # TODO: sntp detection
        pass


class POP3:
    PACKET = b'auth'

    @staticmethod
    def is_pop3(packet: bytes) -> bool:
        return packet.startswith(b'+OK')


class HTTP:
    PACKET = b'\0'

    @staticmethod
    def is_html(packet: bytes) -> bool:
        return b'HTTP' in packet


class SMTP:
    PACKET = b'EHLO'

    @staticmethod
    def is_smtp(packet: bytes) -> bool:
        return packet[:3].isdigit()


def main_loop(host: str, start: int, end: int):
    check = {
        'smtp': lambda x: SMTP.is_smtp(x),
        'dns': lambda x: DNS.is_dns(x),
        'pop3': lambda x: POP3.is_pop3(x),
        'http': lambda x: HTTP.is_html(x)
    }

    protocols = {
        'smtp': SMTP.PACKET,
        'dns': DNS.tcp_query_packet(),
        'pop3': POP3.PACKET,
        'http': HTTP.PACKET
    }
    socket.setdefaulttimeout(0.1)
    for port in range(start, end + 1):
        for protocol, query_packet in protocols.items():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.connect((host, port))
                except (socket.timeout, TimeoutError, OSError):
                    continue
                try:
                    sock.send(query_packet)
                    packet = sock.recv(128)
                    if check[protocol](packet):
                        print(f'{port} {protocol}')
                except socket.error:
                    continue


if __name__ == "__main__":
    args = Args()
    main_loop(args.host, args.start, args.end)
