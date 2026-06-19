import math
from fastapi import Request
import mmh3
from bitarray import bitarray

import math
import mmh3
from bitarray import bitarray


class BloomFilter:

    def __init__(self, expected_items: int, false_positive_rate: float):
        self.size = self._calculate_size(
            expected_items,
            false_positive_rate
        )

        self.hash_count = self._calculate_hash_count(
            self.size,
            expected_items
        )

        self.bit_array = bitarray(self.size)
        self.bit_array.setall(False)

    def add(self, item: str):
        h1 = mmh3.hash(item, 0)
        h2 = mmh3.hash(item, 1)

        for i in range(self.hash_count):
            digest = (h1 + i * h2) % self.size
            self.bit_array[digest] = True

    def contains(self, item: str) -> bool:
        h1 = mmh3.hash(item, 0)
        h2 = mmh3.hash(item, 1)

        for i in range(self.hash_count):
            digest = (h1 + i * h2) % self.size
            if not self.bit_array[digest]:
                return False

        return True

    @staticmethod
    def _calculate_size(n: int, p: float) -> int:
        return int(-(n * math.log(p)) / (math.log(2) ** 2))

    @staticmethod
    def _calculate_hash_count(size: int, n: int) -> int:
        return int((size / n) * math.log(2))


def get_bloom_filter(request: Request):
    return request.app.state.bloom_filter