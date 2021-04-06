import socket
import argparse
from timestamp import Timestamp
from sntp import SNTP


class Client:
    def __init__(self, ntp_server: str):
        self._client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ntp_server = ntp_server

    def run(self):
        data = SNTP.CLIENT_REQUEST
        self._client.sendto(data.encode('utf-8'), (self._ntp_server, 123))
        data, address = self._client.recvfrom(1024)
        if data:
            print(f'Response received from: {address[0]}:{address[1]}')
        timestamp = SNTP.time_from_client_answer(data)
        time = Timestamp.normal_time(timestamp)
        print(f'\tTime: {time}')


def parse_args():
    parser = argparse.ArgumentParser(description='SNTP client')
    parser.add_argument('server', type=str,
                        help='ntp server to request current time')
    return parser.parse_args()


def start():
    args = parse_args()
    client = Client(args.server)
    client.run()


if __name__ == '__main__':
    start()
