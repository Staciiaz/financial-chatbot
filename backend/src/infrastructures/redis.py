from redis.asyncio import Redis as AsyncRedis

from ..config.app import AppConfig


class RedisClient:
    def __init__(self, config: AppConfig):
        self.client = AsyncRedis.from_url(config.redis.url, decode_responses=True)

    def get_client(self):
        return self.client
    
    async def initialize(self):
        await self.client.ping()

    async def close(self):
        await self.client.close()
