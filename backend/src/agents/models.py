from pydantic import BaseModel, Field


class QuestionerResponse(BaseModel):
    question: str = Field(..., description="The sub-question that aim to discover specific aspects of the main question.")
    company: str = Field(..., description="The company the sub-question is focused on.")
    fiscal_years: list[int] = Field(default_factory=list, description="The fiscal years explicitly mentioned in the main question for which the sub-question is relevant.")


class QuestionerResponse(BaseModel):
    sub_questions: list[QuestionerResponse] = Field(default_factory=list, description="A list of sub-questions generated based on the main question and context.")


class SubQuestion(BaseModel):
    company: str = Field(..., description="The company the sub-question is focused on.")
    fiscal_years: list[int] = Field(default_factory=list, description="The fiscal years explicitly mentioned in the main question for which the sub-question is relevant.")
    question: str = Field(..., description="The sub-question that aims to discover specific aspects of the main question.")
    has_financial_data: bool = Field(..., description="Indicates whether the company has financial data available for retrieval.")
    has_document: bool = Field(..., description="Indicates whether the company has relevant document data available for retrieval.")
