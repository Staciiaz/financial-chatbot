from contextlib import AsyncExitStack
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..entities.sql.user import User as UserEntity
from ..infrastructures.postgresql import PostgresqlClient
from ..models.user import User


class UserRepository:
    def __init__(
        self,
        postgresql_client: PostgresqlClient,
    ):
        self.postgresql_client = postgresql_client

    async def create_user(self, user: User, session: AsyncSession = None) -> None:
        """
        Creates a new user in the database.
        """
        async with AsyncExitStack() as stack:
            if session is None:
                # If no session is provided, create a new one
                session = await stack.enter_async_context(self.postgresql_client.create_session())

            user_entity = UserEntity(
                username=user.username,
                password_hash=user.password_hash,
                company=user.company,
                sector=user.sector,
            )
            session.add(user_entity)

    async def get_user_by_username(self, username: str, session: AsyncSession = None) -> Optional[User]:
        """
        Retrieves a user by their username.
        """
        async with AsyncExitStack() as stack:
            if session is None:
                # If no session is provided, create a new one
                session = await stack.enter_async_context(self.postgresql_client.create_session())

            query = select(UserEntity).where(UserEntity.username == username)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return (
                User(
                    username=user.username,
                    password_hash=user.password_hash,
                    company=user.company,
                    sector=user.sector,
                )
                if user else None
            )

