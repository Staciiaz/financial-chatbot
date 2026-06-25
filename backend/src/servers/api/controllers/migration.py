from typing import Annotated

from fastapi import File

from ....services.migration import MigrationService


class MigrationController:
    def __init__(
        self,
        migration_svc: MigrationService,
    ):
        self.migration_svc = migration_svc
    
    async def import_pinecone_index(
        self,
        file: Annotated[bytes, File()],
    ):
        await self.migration_svc.import_pinecone_index(file)
        return {"message": "Pinecone index imported successfully"}
