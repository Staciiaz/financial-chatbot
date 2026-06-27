from src.config.app import AppConfig

from ..infrastructures.pinecone import PineconeClient
from ..infrastructures.postgresql import PostgresqlClient
from ..infrastructures.redis import RedisClient
from ..repositories.document import DocumentRepository
from ..repositories.financial import FinancialRepository
from ..repositories.user import UserRepository
from ..services.agent import AgentService
from ..services.auth import AuthService
from ..services.migration import MigrationService


class Container:
    def __init__(self, config: AppConfig):
        """
        Initialize the container and its components.

        Potential improvement: Should use dependency injection library to manage components and their dependencies.
        """
        # Initialize infrastructures
        self.redis_client = RedisClient(config)
        self.pinecone_client = PineconeClient(config)
        self.postgresql_client = PostgresqlClient(config)
        # Initialize repositories
        self.document_repo = DocumentRepository(
            config=config,
            pinecone_client=self.pinecone_client,
        )
        self.financial_repo = FinancialRepository(
            postgresql_client=self.postgresql_client,
        )
        self.user_repo = UserRepository(
            postgresql_client=self.postgresql_client,
        )
        # Initialize services
        self.migration_svc = MigrationService(
            document_repo=self.document_repo,
        )
        self.auth_svc = AuthService(
            config=config,
            redis=self.redis_client,
            user_repo=self.user_repo,
        )
        self.agent_svc = AgentService(
            document_repo=self.document_repo,
            financial_repo=self.financial_repo,
        )

    async def initialize(self):
        """
        Initialize the container and its components.
        """
        # Initialize infrastructures
        await self.redis_client.initialize()
        await self.postgresql_client.initialize()
        # Initialize repositories
        await self.document_repo.initialize()

    async def close(self):
        """
        Close the container and its components.
        """
        # Close repositories
        await self.document_repo.close()
        # Close infrastructures
        await self.redis_client.close()
        await self.pinecone_client.close()
        await self.postgresql_client.close()
