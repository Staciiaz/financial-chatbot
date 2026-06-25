from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .pinecone import PineconeConfig
from .postgresql import PostgresqlConfig


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_max_split=1,
        env_nested_delimiter="_",
    )

    host: str = Field(
        default="0.0.0.0",
        description="The host address for the server to bind to.",
    )
    port: int = Field(
        default=8000,
        description="The port number for the server to listen on.",
    )

    jwt_secret_key: str = Field(
        description="The secret key used for signing and verifying JWT tokens.",
    )

    pinecone: PineconeConfig = Field(
        default_factory=PineconeConfig,
        description="Configuration settings for the Pinecone service.",
    )

    postgresql: PostgresqlConfig = Field(
        default_factory=PostgresqlConfig,
        description="Configuration settings for the PostgreSQL database.",
    )

    openai_api_key: str = Field(
        description="The API key for authenticating with the OpenAI service.",
    )
