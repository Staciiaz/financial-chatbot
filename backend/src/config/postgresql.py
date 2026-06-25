from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresqlConfig(BaseSettings):
    host: str = Field(
        description="The host address for the PostgreSQL database.",
    )
    port: int = Field(
        description="The port number for the PostgreSQL database.",
    )
    user: str = Field(
        description="The username for authenticating with the PostgreSQL database.",
    )
    password: str = Field(
        description="The password for authenticating with the PostgreSQL database.",
    )
    database: str = Field(
        description="The name of the PostgreSQL database to connect to.",
    )
