import math
from threading import Lock

import mmh3
from bitarray import bitarray


class BloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float):
        if expected_items <= 0:
            raise ValueError("expected_items must be greater than zero")
        if not 0 < false_positive_rate < 1:
            raise ValueError("false_positive_rate must be between 0 and 1")

        self.size = max(
            1,
            int(
                -(expected_items * math.log(false_positive_rate))
                / (math.log(2) ** 2)
            ),
        )
        self.hash_count = max(
            1,
            int((self.size / expected_items) * math.log(2)),
        )
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(False)
        self._lock = Lock()

    def add(self, item: str) -> None:
        with self._lock:
            for digest in self._digests(item):
                self.bit_array[digest] = True

    def contains(self, item: str) -> bool:
        with self._lock:
            return all(self.bit_array[digest] for digest in self._digests(item))

    def _digests(self, item: str):
        first = mmh3.hash(item, 0)
        second = mmh3.hash(item, 1)
        for index in range(self.hash_count):
            yield (first + index * second) % self.size
