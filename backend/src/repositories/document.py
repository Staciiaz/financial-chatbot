from typing import Optional

from langchain_openai import OpenAIEmbeddings

from ..config.app import AppConfig
from ..infrastructures.pinecone import PineconeClient
from ..models.document import Document

# This dictionary maps company names to their corresponding 10-K filing PDF filenames.
# It is used to identify which companies have relevant document data available for retrieval.
DOCUMENTS = {
    "Google": "Alphabet_10K_FY2025.pdf",
    "Amazon": "Amazon_10K_FY2025.pdf",
    "Apple": "Apple_10K_FY2025.pdf",
    "Meta": "Meta_10K_FY2025.pdf",
}


class DocumentRepository:
    def __init__(
        self,
        config: AppConfig,
        pinecone_client: PineconeClient,
    ):
        self.config = config
        self.pc = pinecone_client.get_client()
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=512,
        )

    async def initialize(self):
        self.dense_index = await self.pc.index(host=self.config.pinecone.index_host)

    async def close(self):
        await self.dense_index.close()
        
    async def upsert_vectors(self, vectors: list[dict]) -> None:
        if not vectors:
            raise ValueError("Vectors list is empty")

        try:
            # Upsert vectors in batches of 100
            for batch in [vectors[i:i + 100] for i in range(0, len(vectors), 100)]:
                await self.dense_index.upsert(
                    vectors=batch,
                    namespace="__default__",
                )
        except Exception as e:
            raise RuntimeError(f"Failed to upsert vectors: {str(e)}")
        
    async def query_documents(self, query_text: str, company: Optional[str] = None, top_k: int = 5) -> list[Document]:
        try:
            query_vector = await self.embedding_model.aembed_documents([query_text])
            results = await self.dense_index.query(
                vector=query_vector[0],
                top_k=top_k,
                filter={"source": DOCUMENTS.get(company, "")} if company else None, # Filter by company if provided
                include_metadata=True,
                namespace="__default__",
            )

            return [
                Document(
                    id=match.id,
                    score=match.score,
                    page=match.metadata.get("page", 0),
                    page_label=match.metadata.get("page_label", ""),
                    source=match.metadata.get("source", ""),
                    text=match.metadata.get("text", ""),
                )
                for match in results.matches
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to query vectors: {str(e)}")
