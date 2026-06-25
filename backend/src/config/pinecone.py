from pydantic import Field
from pydantic_settings import BaseSettings


class PineconeConfig(BaseSettings):
    host: str = Field(
        description="The host address for the Pinecone service.",
    )
    port: int = Field(
        description="The port number for the Pinecone service.",
    )
    api_key: str = Field(
        description="The API key for authenticating with the Pinecone service.",
    )
