from fastapi import Request

from app.algorithms.base_encoder import Base62Encoder
from app.algorithms.bloom_filter import BloomFilter
from app.algorithms.distributed_id import DistributedIDGenerator
from app.algorithms.redis_bloomfilter import RedisBloomFilter


def get_base62_encoder(request: Request) -> Base62Encoder:
    return request.app.state.base62_encoder


def get_bloom_filter(request: Request) -> BloomFilter:
    return request.app.state.bloom_filter


def get_redis_bloom_filter(request: Request) -> RedisBloomFilter:
    return request.app.state.redis_bloom_filter


def get_distributed_id_generator(request: Request) -> DistributedIDGenerator:
    return request.app.state.distributed_id_generator
