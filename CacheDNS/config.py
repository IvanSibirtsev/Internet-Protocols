class Config:
    def __init__(self):
        self.timeout = 0.5
        self.buffer_size = 1024
        self.cache_dump = 'dns.cache'

    @property
    def local_server_address(self) -> tuple[str, int]:
        return 'localhost', 53

    @property
    def forwarder_address(self) -> tuple[str, int]:
        return '8.8.8.8', 53
