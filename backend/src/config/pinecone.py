from pydantic import Field
from pydantic_settings import BaseSettings


class PineconeConfig(BaseSettings):
    host: str = Field(
        default="https://api.pinecone.io",
        description="The host address for the Pinecone service.",
    )
    api_key: str = Field(
        description="The API key for authenticating with the Pinecone service.",
    )
    index_host: str = Field(
        description="The host address for the Pinecone index.",
    )
