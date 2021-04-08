from decimal import Decimal
import time


class Timestamp:
    """https://tools.ietf.org/html/rfc868"""
    TIME_SINCE_01_01_1900 = 2208988800
    BITE_OFFSET = 2 ** 32

    @staticmethod
    def time_with_delta(time_delta: float) -> int:
        current_time = time.time() + Timestamp.TIME_SINCE_01_01_1900
        wrong_time = current_time + time_delta
        return int(Decimal(wrong_time) * Timestamp.BITE_OFFSET)

    @staticmethod
    def normal_time(timestamp: int) -> str:
        normal_time = timestamp - Timestamp.TIME_SINCE_01_01_1900
        return time.ctime(normal_time)
