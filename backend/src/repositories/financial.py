from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from ..infrastructures.postgresql import PostgresqlClient
from ..models.financial_data import FinancialData


class FinancialRepository:
    def __init__(
        self,
        postgresql_client: PostgresqlClient,
    ):
        self.postgresql_client = postgresql_client

    async def list_company_names(self, session: AsyncSession = None) -> list[str]:
        """
        Retrieves a list of distinct company names from the financial_data table.

        Returns:
            list[str]: A list of distinct company names.
        """
        async with AsyncExitStack() as stack:
            if session is None:
                # If no session is provided, create a new one
                session = await stack.enter_async_context(self.postgresql_client.create_session())
            
            result = await session.execute(text("SELECT DISTINCT company FROM financial_data"))
            rows = result.fetchall()
            return [row[0] for row in rows]

    async def raw_query(self, query: str, args: dict = None, session: AsyncSession = None) -> list[FinancialData]:
        """
        Executes a raw SQL query against the financial_data table.

        Args:
            query (str): The raw SQL query to execute.

        Returns:
            list[FinancialData]: A list of FinancialData instances matching the query results.
        """
        if "from financial_data" not in query.lower():
            # Simple validation to ensure the query is targeting the financial_data table
            # Note: This is a basic check and may not cover all cases. For production, consider using a more robust SQL parser or ORM.
            raise ValueError("The SQL query must include 'FROM financial_data'.")

        async with AsyncExitStack() as stack:
            if session is None:
                # If no session is provided, create a new one
                session = await stack.enter_async_context(self.postgresql_client.create_session())
            
            result = await session.execute(text(query), args)
            rows = result.fetchall()

            # Map the result rows to FinancialData instances
            return [FinancialData(**dict(zip(FinancialData.model_fields.keys(), row))) for row in rows]
