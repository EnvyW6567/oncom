import os

import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


async def get_redis():
    return await redis.from_url(REDIS_URL)
