import time
from socket import socket, AF_INET, SOCK_DGRAM, timeout
from typing import NoReturn

from request_handler import RequestHandler
from config import Config
from cache import Cache


class Server:
    def __init__(self, config: Config, handler: RequestHandler):
        self._config = config
        self._handler = handler
        self._server = self._configure_server()

    def _configure_server(self) -> socket:
        server = socket(AF_INET, SOCK_DGRAM)
        server.settimeout(2)
        server.bind(self._config.local_server_address)
        return server

    def run(self) -> NoReturn:
        while True:
            data, address = self._receive_request()
            response = self._handle_request(data)
            self._server.sendto(response, address)

    def _receive_request(self) -> tuple[bytes, str]:
        try:
            return self._server.recvfrom(self._config.buffer_size)
        except timeout:
            time.sleep(0.01)
            return self._receive_request()
        except Exception as e:
            self._server.close()
            print(e)
            exit()

    def _handle_request(self, data: bytes) -> bytes:
        return self._handler.handle_query(data)


def main() -> NoReturn:
    config = Config()
    cache = Cache.from_dump(config.cache_dump)
    request_handler = RequestHandler(config, cache)
    try:
        server = Server(config, request_handler)
        server.run()
    except KeyboardInterrupt:
        cache.dump_to_file(config.cache_dump)


if __name__ == '__main__':
    main()
