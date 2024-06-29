from typing import Any
from utils import AgentState, ConfigManager, LLM
from db_manager import DBManager
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
import logging
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class Node:
    def __init__(self) -> None:
        self.config = ConfigManager()
        self.db = DBManager(self.config["database"])
        self.llm = LLM("togetherAI")
        # self.llm = LLM("openAI")
        # self.llm = LLM("cluade")
        logger.info("Node1 (Text2SQL) initialized")

    def forward(self, state: AgentState):
        logger.info("Forward method called with state: %s", state)
        question = state.get("question")
        parser = JsonOutputParser(pydantic_object=TextToSQL)
        
        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{user_prompt}\nThe Database schema of Tables and their first row values are: {db_schema}",
            input_variables=["user_prompt" ,"db_schema"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.llm | parser
        answer = chain.invoke({"user_prompt": question, "db_schema": self.db.get_db_head()})
        query = answer["sql_query"]
        logger.info("SQL query generated: %s", query)
        results = self.db.query(query)
        df = pd.DataFrame(results)
        df.to_csv('data.csv', index=False)
        # csv_path = os.path.join("outputs", "data.csv")
        csv_path = "data.csv"
        logger.info("Query results saved to CSV: %s", csv_path)
        
        state["text2sql_results"] = {"query": query, "csv_path": csv_path}
        logger.info("State updated with text2sql results: %s", state["text2sql_results"])
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    
class TextToSQL(BaseModel):
    sql_query: str = Field(description="the sql query to be executed")
    
if __name__ == "__main__":
    c = Node()
    print(c())
