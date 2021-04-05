import argparse
import socket
import sys

MAX_PORT = 65535


class Args:
    def __init__(self):
        self.host, self.start, self.end = self.parse_args()

    @staticmethod
    def parse_args() -> tuple[str, int, int]:
        parser = argparse.ArgumentParser(description='TCP port scanner.')
        parser.add_argument('ports', type=str,
                            help='port or range of ports example: 1..100')
        parser.add_argument('-host', type=str, dest='host',
                            default='localhost', help='host to scan')
        args = parser.parse_args()
        try:
            if '..' in args.ports:
                start, end = args.ports.split('..')
                start, end = int(start), int(end)
            else:
                start, end = int(args.ports), int(args.ports)
        except ValueError:
            print('Port number must be integer')
            sys.exit()
        if end > MAX_PORT:
            print('Port numbers must be less than 65535')
            sys.exit()
        if start > end:
            print('Invalid arguments')
            sys.exit()
        try:
            socket.gethostbyname(args.host)
        except socket.gaierror:
            print(f'Invalid host {args.host}')
            sys.exit()
        return args.host, start, end


def port_scan(args: Args):
    for port in range(args.start, args.end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.01)
            result = sock.connect_ex((args.host, port))
            if result == 0:
                spaces = ' ' * (2 + (len(str(MAX_PORT)) - len(str(port))))
                print(f'Port {port}' + spaces + 'is open')


def main():
    args = Args()
    port_scan(args)


if __name__ == '__main__':
    main()
