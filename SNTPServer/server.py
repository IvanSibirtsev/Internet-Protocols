import argparse
import socket
from sntp import SNTP


class Server:
    _IP = '127.0.0.1'
    _PORT = 123
    _BUFFER_SIZE = 4096

    def __init__(self, time_delta: float):
        self.time_delta = time_delta
        self._server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._server.bind(('localhost', self._PORT))
        print(f'Server start on {self._IP}:{self._PORT}')

    def run(self):
        while True:
            data = self._server.recvfrom(self._BUFFER_SIZE)
            received_packet, address = data[0], data[1]
            print(f'new client – {address[0]}:{address[1]}')
            sntp = SNTP(self.time_delta)
            sntp.analise_packet(received_packet)
            packet = sntp.get_server_packet()
            self._server.sendto(packet, address)


def parse_args():
    parser = argparse.ArgumentParser(description='SNTP server, that allows '
                                                 'to send time with offset')
    parser.add_argument('-o', '--offset', action='store', default=1858623, type=int,
                        dest='time_offset',
                        help='Time offset to right time in seconds. '
                             'Can be positive or negative number')
    return parser.parse_args()


def start() -> None:
    args = parse_args()
    server = Server(args.time_offset)
    server.run()


if __name__ == '__main__':
    start()
