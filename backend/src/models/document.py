from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str = Field(..., description="Unique identifier for the document")
    score: float = Field(..., description="Relevance score of the document")
    page: int = Field(..., description="Page number where the document is located")
    page_label: str = Field(..., description="Label of the page where the document is located")
    source: str = Field(..., description="Source file of the document")
    text: str = Field(..., description="Text content of the document")
