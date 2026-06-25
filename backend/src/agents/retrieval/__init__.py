import operator
from typing import Annotated, TypedDict

from langgraph.graph import START, StateGraph

from ...models.document import Document
from ...models.financial_data import FinancialData
from ...repositories.document import DocumentRepository
from ...repositories.financial import FinancialRepository


class InputState(TypedDict):
    question: str
    company: str
    fiscal_years: list[int]
    has_document: bool
    has_financial_data: bool


class OutputState(TypedDict):
    related_documents: Annotated[list[Document], operator.add]
    related_financial_data: Annotated[list[FinancialData], operator.add]


class State(InputState, OutputState):
    pass


class RetrievalAgent:
    def __init__(
        self,
        document_repo: DocumentRepository,
        financial_repo: FinancialRepository,
    ):
        self.document_repo = document_repo
        self.financial_repo = financial_repo
        self.build_graph()

    def build_graph(self):
        graph_builder = StateGraph(State, input_schema=InputState, output_schema=OutputState)
        graph_builder.add_node("initialize", self.initialize_node)
        graph_builder.add_node("get_financial_data", self.get_financial_data_node)
        graph_builder.add_node("get_relevant_document", self.get_relevant_document_node)
        graph_builder.add_node("finalize", self.finalize_node)
        graph_builder.add_edge(START, "initialize")
        graph_builder.add_edge("initialize", "get_financial_data")
        graph_builder.add_edge("initialize", "get_relevant_document")
        graph_builder.add_edge("get_financial_data", "finalize")
        graph_builder.add_edge("get_relevant_document", "finalize")
        self.graph = graph_builder.compile()

    async def get_financial_data_node(self, state: State) -> State:
        """
        Retrieves financial data for the specified company and fiscal years.
        """
        sql_query = f"SELECT * FROM financial_data WHERE company = :company AND year = ANY(:years)"
        results = await self.financial_repo.raw_query(sql_query, args={"company": state["company"], "years": tuple(state["fiscal_years"])})
        return {"related_financial_data": results}
    
    async def get_relevant_document_node(self, state: State) -> State:
        """
        Retrieves relevant documents for the specified question and company.
        """
        results = await self.document_repo.query_documents(state["question"], state["company"])
        return {"related_documents": results}

    async def initialize_node(self, state: State) -> State:
        return {}
    
    async def finalize_node(self, state: State) -> State:
        return {}
