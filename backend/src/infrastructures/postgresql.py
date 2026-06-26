from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from ..config.app import AppConfig
from ..entities.sql.user import Base


class PostgresqlClient:
    def __init__(self, config: AppConfig):
        self.config = config

    @asynccontextmanager
    async def create_session(self) -> AsyncGenerator[AsyncSession, None]:
        Session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )
        async with Session() as session:
            try:
                yield session
                await session.commit() # Commit the transaction after the block of code using the session is executed
                session.expunge_all()  # Detach all objects from the session to prevent issues with expired objects after commit
            except Exception as e:
                # Rollback the transaction in case of an error
                await session.rollback()
                raise e
            finally:
                # Close the session after the block of code using the session is executed
                await session.close()

    async def initialize(self):
        conn_str = f"postgresql+asyncpg://{self.config.postgresql.user}:{self.config.postgresql.password}@{self.config.postgresql.host}:{self.config.postgresql.port}/{self.config.postgresql.database}"
        self.engine = create_async_engine(conn_str)
        # Create the tables in the database if they don't exist
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.engine.dispose()
