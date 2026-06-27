from pydantic import Field
from pydantic_settings import BaseSettings


class JwtConfig(BaseSettings):
    access_token_secret: str = Field(
        description="The secret key for signing JWT access tokens.",
    )
    refresh_token_secret: str = Field(
        description="The secret key for signing JWT refresh tokens.",
    )
