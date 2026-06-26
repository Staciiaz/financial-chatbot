import operator
from typing import Annotated, TypedDict

from langchain.messages import AIMessageChunk, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.types import Send
from pydantic import TypeAdapter

from ..models.document import Document
from ..models.financial_data import FinancialData
from ..repositories.document import DocumentRepository
from ..repositories.financial import FinancialRepository
from .models import QuestionerResponse, SubQuestion
from .prompts import ANSWERER_PROMPT, QUESTIONER_PROMPT
from .retrieval import RetrievalAgent


class State(TypedDict):
    main_question: str
    sub_questions: list[SubQuestion]
    related_documents: Annotated[list[Document], operator.add]
    related_financial_data: Annotated[list[FinancialData], operator.add]
    answer: str


class OrchestratorAgent:
    def __init__(
        self,
        document_repo: DocumentRepository,
        financial_repo: FinancialRepository,
    ):
        self.document_repo = document_repo
        self.financial_repo = financial_repo
        # Initialize two separate LLMs for question generation and answer generation
        self.questioner_llm = ChatOpenAI(
            model="gpt-5-nano",
            reasoning_effort="low",
            tags=["questioner"]
        )
        self.answerer_llm = ChatOpenAI(
            model="gpt-5-nano",
            reasoning_effort="low",
            tags=["answerer"],
        )
        self.retrieval_agent = RetrievalAgent(
            document_repo=document_repo,
            financial_repo=financial_repo,
        )
        self.build_graph()

    def build_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("initialize", self.initialize_node)
        graph_builder.add_node("generate_sub_questions", self.generate_sub_questions_node)
        graph_builder.add_node("retrieval_agent", self.retrieval_agent.graph)
        graph_builder.add_node("generate_answer", self.generate_answer_node)
        graph_builder.add_node("finalize", self.finalize_node)
        graph_builder.add_edge(START, "initialize")
        graph_builder.add_edge("initialize", "generate_sub_questions")
        graph_builder.add_conditional_edges("generate_sub_questions", self.assign_retrieval_agent)
        graph_builder.add_edge("retrieval_agent", "generate_answer")
        graph_builder.add_edge("generate_answer", "finalize")
        self.graph = graph_builder.compile()

    async def initialize_node(self, state: State) -> State:
        return {}
    
    async def generate_sub_questions_node(self, state: State) -> State:
        """
        Generates sub-questions based on the main question and the list of available companies.
        """
        company_names = await self.financial_repo.list_company_names()
        structured_llm = self.questioner_llm.with_structured_output(QuestionerResponse)
        response: QuestionerResponse = await structured_llm.ainvoke(
            input=[
                HumanMessage(
                    content=QUESTIONER_PROMPT.format(
                        company_list=", ".join(company_names),
                        main_question=state["main_question"],
                    )
                ),
            ],
        )
        return {
            "sub_questions": [
                SubQuestion(
                    company=q.company,
                    fiscal_years=q.fiscal_years,
                    question=q.question,
                    has_financial_data=q.company in company_names,
                    has_document=q.company in ["Google", "Amazon", "Apple", "Meta"], # Only these companies have documents in the database for now
                )
                for q in response.sub_questions
            ]
        }
    
    async def assign_retrieval_agent(self, state: State):
        """
        Assigns the retrieval agent to each sub-question based on the availability of financial data and documents.
        """
        return [
            Send(
                node="retrieval_agent",
                arg={
                    "question": q.question,
                    "company": q.company,
                    "fiscal_years": q.fiscal_years,
                    "has_document": q.has_document,
                    "has_financial_data": q.has_financial_data,
                },
            )
            for q in state["sub_questions"]
        ]
    
    async def generate_answer_node(self, state: State) -> State:
        """
        Generates an answer to the main question based on the related documents and financial data retrieved by the RetrievalAgent.
        """
        response = await self.answerer_llm.ainvoke(
            input=[
                HumanMessage(
                    content=ANSWERER_PROMPT.format(
                        main_question=state["main_question"],
                        related_financial_data=(
                            TypeAdapter(list[FinancialData]).dump_json(state["related_financial_data"]).decode("utf-8")
                            if state["related_financial_data"] else "No relevant financial data found."
                        ),
                        related_documents=(
                            TypeAdapter(list[Document]).dump_json(state["related_documents"]).decode("utf-8")
                            if state["related_documents"] else "No relevant documents found."
                        ),
                    )
                )
            ]
        )
        return {"answer": str(response.text)}
    
    async def finalize_node(self, state: State) -> State:
        return {}
    
    async def ask_question(self, main_question: str) -> str:
        """
        Asks the agent a question and returns the final answer.

        Args:
            main_question (str): The main question to be asked.

        Returns:
            str: The final answer generated by the agent based on the retrieved information.
        """
        input_state = {
            "main_question": main_question,
        }
        output_state = await self.graph.ainvoke(input_state)
        return output_state["answer"]
    
    async def ask_question_stream(self, main_question: str):
        """
        Asks the agent a question and streams the final answer as it is generated.

        Args:
            main_question (str): The main question to be asked.

        Yields:
            str: The partial answer generated by the agent as it is being streamed.
        """
        async for mode, chunk in self.graph.astream(
            input={
                "main_question": main_question,
            },
            stream_mode=["messages", "values"],
        ):
            if mode == "messages":
                message, metadata = chunk
                if isinstance(message, AIMessageChunk):
                    if "answerer" in metadata["tags"]:
                        # Stream the answerer LLM's output as it is generated
                        yield str(message.text)
