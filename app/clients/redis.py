from redis import Redis

def get_redis_client() -> Redis:
    redis_client = Redis(
        host='localhost',
        port=6379,
        decode_responses=True,
        password='test12345'
    )
    return redis_client