from threading import Lock

from redis import Redis

from app.core.exceptions import IdSpaceExhaustedError


class DistributedIDGenerator:
    def __init__(
        self,
        redis_client: Redis,
        *,
        key: str,
        block_size: int,
        max_id: int,
    ):
        self.redis_client = redis_client
        self.key = key
        self.block_size = block_size
        self.max_id = max_id
        self._next_id = 1
        self._block_end = 0
        self._lock = Lock()

    def _reserve_block(self) -> None:
        block_end = int(self.redis_client.incrby(self.key, self.block_size))
        block_start = block_end - self.block_size + 1

        if block_start > self.max_id:
            raise IdSpaceExhaustedError("Short-code ID space has been exhausted")

        self._next_id = block_start
        self._block_end = min(block_end, self.max_id)

    def next_id(self) -> int:
        with self._lock:
            if self._next_id > self._block_end:
                self._reserve_block()

            value = self._next_id
            self._next_id += 1
            return value
