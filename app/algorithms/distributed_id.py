from threading import Lock

from fastapi import Request
from redis import Redis


class DistributedIDGenerator:
    ID_SPACE = 62 ** 7

    def __init__(
        self,
        redis_client: Redis,
        key: str = "url_shortener:id_counter",
        block_size: int = 10_000,
    ):
        if block_size <= 0:
            raise ValueError("block_size must be greater than zero")

        self.redis_client = redis_client
        self.key = key
        self.block_size = block_size
        self._next_id = 1
        self._block_end = 0
        self._lock = Lock()

    def _reserve_block(self) -> None:
        block_end = int(self.redis_client.incrby(self.key, self.block_size))
        block_start = block_end - self.block_size + 1

        if block_start >= self.ID_SPACE:
            raise RuntimeError("Seven-character Base62 ID space has been exhausted.")

        self._next_id = block_start
        self._block_end = min(block_end, self.ID_SPACE - 1)

    def next_id(self) -> int:
        with self._lock:
            if self._next_id > self._block_end:
                self._reserve_block()

            value = self._next_id
            self._next_id += 1
            return value


def get_distributed_id_generator(request: Request) -> DistributedIDGenerator:
    return request.app.state.distributed_id_generator
