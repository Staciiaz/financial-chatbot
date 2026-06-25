import gzip
import json

from ..repositories.document import DocumentRepository


class MigrationService:
    def __init__(
        self,
        document_repo: DocumentRepository,
    ):
        self.document_repo = document_repo

    async def import_pinecone_index(self, file: bytes):
        """
        Imports a Pinecone index from a gzip-compressed JSON file.
        The file is expected to contain JSON lines, where each line represents a vector with its metadata.
        The service will decompress the file, parse the JSON lines, and upsert the vectors into the Pinecone index.
        It also filters out duplicate document texts to avoid redundant entries in the index.
        """
        if file[:2] != b'\x1f\x8b':
            raise ValueError("Invalid gzip file")
        
        decompressed_data = gzip.decompress(file).decode('utf-8')

        # Process the decompressed data
        vector_data = []
        document_texts = set()  # To track unique document texts
        for line in decompressed_data.splitlines():
            if line.strip():
                try:
                    vector: dict = json.loads(line)
                    vector.pop('namespace', None)  # Remove the namespace field if it exists

                    metadata: dict = vector.get('metadata', {})
                    document_text: str = metadata.get('text', '')
                    document_source: str = metadata.get('source', '')
                    metadata['source'] = document_source.split("/")[-1]  # Extract filename from path

                    # Filter out duplicate document texts
                    if document_text is not None and document_text not in document_texts:
                        document_texts.add(document_text)
                        vector_data.append(vector)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON line: {line}. Error: {str(e)}")

        print(f"Importing {len(vector_data)} unique vectors into the Pinecone index...")
        await self.document_repo.upsert_vectors(vector_data)
        return "Pinecone index imported successfully"
