from pydantic import BaseModel, Field


class RedisConfig(BaseModel):
    url: str = Field(
        description="Redis connection URL",
    )
