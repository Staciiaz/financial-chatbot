from pinecone import AsyncPinecone

from ..config.app import AppConfig


class PineconeClient:
    def __init__(self, config: AppConfig):
        self.client = AsyncPinecone(
            api_key=config.pinecone.api_key,
            host=config.pinecone.host,
        )

    def get_client(self):
        return self.client

    async def close(self):
        await self.client.close()
