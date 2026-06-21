from fastapi import Request
from redis import Redis, ResponseError

class RedisBloomFilter:

    def __init__(self, redis_client: Redis, key: str):
        self.redis_client = redis_client
        self.key = key


    def initialize(self, error_rate: float, capacity: int):
        try:
            self.redis_client.execute_command(
                "BF.RESERVE", self.key, error_rate, capacity
            )
        except ResponseError as e:
            if "item exists" not in str(e).lower():
                raise RuntimeError(
                    f"Failed to initialize Redis Bloom filter: {e}"
                ) from e
    
    def add(self, item: str):
        self.redis_client.execute_command('BF.ADD', self.key, item)
    

    def contains(self, item: str) -> bool:
        return bool(
            self.redis_client.execute_command('BF.EXISTS', self.key, item)
        )
    


def get_redis_bloom_filter(request: Request) -> RedisBloomFilter:
    return request.app.state.redis_bloom_filter