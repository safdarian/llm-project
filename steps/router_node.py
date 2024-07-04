from typing import Any
from utils import AgentState, LLM
from langchain_core.pydantic_v1 import BaseModel, Field
import logging
from logging_config import setup_logging

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal


setup_logging()
logger = logging.getLogger(__name__)


class Node:
    def __init__(self) -> None:
        self.llm = LLM("togetherAI")

    def forward(self, state: AgentState):
        # Define the router prompt template
        router_prompt_template = """You are a routing assistant for a database query system. Your task is to decide whether the given question is relevant to the database schema described below. If the question is relevant to the database schema, you should route the question to the "Text2SQL" tool. If the question is not relevant to the database schema, route it to "None".

Database Schema:
Regions(StateCode, State, Region)
StoreLocations(StoreID, CityName, County, StateCode, State, Type, Latitude, Longitude, AreaCode, Population, HouseholdIncome, MedianIncome, LandArea, WaterArea, TimeZone)
Customers(CustomerID, CustomerNames)
Products(ProductID, ProductName)
SalesTeam(SalesTeamID, SalesTeam, Region)
SalesOrders(OrderNumber, SalesChannel, WarehouseCode, ProcuredDate, OrderDate, ShipDate, DeliveryDate, CurrencyCode, _SalesTeamID, _CustomerID, _StoreID, _ProductID, OrderQuantity, DiscountApplied, UnitPrice, UnitCost)

Based on the above database schema, decide whether the given question should be routed to "Text2SQL" or "None".
Give me only and only the name of the tool you chose and nothing more. If there are no chose tool, give me back the string None.

{output_instructions}

Question: {question}

Response: 
        """

        # Create the prompt
        prompt = ChatPromptTemplate.from_template(
            template=router_prompt_template,
        )

        # Define the ChosenTool class for the parser
        class ChosenTool(BaseModel):
            tool_name: Literal["None", "Text2SQL"] = Field(
                description="the tool that was chosen by LLM in question routing stage"
            )

        # Create the parser
        question_router_parser = PydanticOutputParser(pydantic_object=ChosenTool)

        # Get format instructions for the parser
        format_instructions = question_router_parser.get_format_instructions()

        # Combine the prompt, LLM, and parser into the question router
        question_router = prompt | self.llm | question_router_parser

        question = state["question"]
        try:
            response = question_router.invoke(
                {
                    "question": question,
                    "output_instructions": question_router_parser.get_format_instructions(),
                }
            )
            logger.info("Question Router: " + response)
        except Exception:
            print("Exception in getting response")
            return "LLMFallback"
        try:
            chosen_tool = response.tool_name.lower()
        except Exception:
            return "LLMFallback"

        if chosen_tool == "none":
            print("---No tool called---")
            return "LLMFallback"

        if chosen_tool == "text2sql":
            print("---Routing to Text2SQL---")
            return "Text2SQL"

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)


if __name__ == "__main__":
    c = Node()
    print(c())
