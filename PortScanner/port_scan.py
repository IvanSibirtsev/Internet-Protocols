import argparse
import socket
import sys


MAX_PORT = 65535


def parse_args() -> tuple[int, int]:
    parser = argparse.ArgumentParser(description='TCP port scanner.')
    parser.add_argument('ports', type=str, help='port or range of ports '
                                                'example: 1..100')
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
    return start, end


def port_scan(start: int, end: int):
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.01)
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                spaces = ' ' * (2 + (len(str(MAX_PORT)) - len(str(port))))
                print(f'Port {port}' + spaces + 'is open')


def main():
    start, end = parse_args()
    port_scan(start, end)


if __name__ == '__main__':
    main()
