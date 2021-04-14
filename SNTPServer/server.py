import argparse
import socket
from sntp import SNTP


class Server:
    _IP = '127.0.0.1'
    _PORT = 123
    _BUFFER_SIZE = 1024

    def __init__(self, server: socket.socket, time_delta: float):
        self.time_delta = time_delta
        self._server = server
        print(f'Server start on {self._IP}:{self._PORT}')

    def run(self):
        while True:
            try:
                data = self._server.recvfrom(self._BUFFER_SIZE)
            except KeyboardInterrupt:
                self._server.close()
                print('server stop')
                break
            received_packet, address = data[0], data[1]
            print(f'new client – {address[0]}:{address[1]}')
            sntp = SNTP(self.time_delta)
            sntp.analise_packet(received_packet)
            packet = sntp.get_server_packet()
            self._server.sendto(packet, address)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='SNTP server, that allows to send time with offset')
    parser.add_argument('-d', '--delay', action='store', default=0,
                        type=int, dest='delay',
                        help='Time offset to right time in seconds. '
                             'Can be positive or negative number')
    return parser.parse_args()


def start():
    args = parse_args()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind(('localhost', 123))
        Server(server, args.delay).run()


if __name__ == '__main__':
    start()
