from app.algorithms.distributed_id import DistributedIDGenerator


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, int] = {}
        self.calls = 0

    def incrby(self, key: str, amount: int) -> int:
        self.calls += 1
        self.values[key] = self.values.get(key, 0) + amount
        return self.values[key]


def test_generator_reserves_ids_in_blocks() -> None:
    redis = FakeRedis()
    generator = DistributedIDGenerator(
        redis,
        key="ids",
        block_size=3,
        max_id=100,
    )

    assert [generator.next_id() for _ in range(4)] == [1, 2, 3, 4]
    assert redis.calls == 2


def test_two_generators_receive_non_overlapping_blocks() -> None:
    redis = FakeRedis()
    first = DistributedIDGenerator(
        redis,
        key="ids",
        block_size=2,
        max_id=100,
    )
    second = DistributedIDGenerator(
        redis,
        key="ids",
        block_size=2,
        max_id=100,
    )

    assert {first.next_id(), first.next_id()} == {1, 2}
    assert {second.next_id(), second.next_id()} == {3, 4}
