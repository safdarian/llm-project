from typing import Any
from utils import State, ConfigManager, LLM
from langchain_together import Together
import re
import os
from db_manager import DBManager
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_together import Together
import pandas as pd
from langchain_core.output_parsers import StrOutputParser

class Node:
    def __init__(self) -> None:
        self.config = ConfigManager()
        self.db = DBManager(self.config["database"])
        #self.llm = LLM("togetherAI")
        self.llm = LLM("openAI")
        #self.llm = LLM("localMLX")
        
    def forward(self, state: State):
        question = state.get("question")
        parser = JsonOutputParser(pydantic_object=TextToSQL)
        
        prompt = PromptTemplate(
                template="Answer the user query.\n{format_instructions}\n{user_prompt}\n{db_schema}",
                input_variables=["user_prompt" ,"db_schema"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )
        chain = prompt | self.llm | parser
        answer = chain.invoke({"user_prompt": question, "db_schema": self.db.get_schema()})
        query = answer["sql_query"]
        results = self.db.query(query)
        df = pd.DataFrame(results)
        df.to_csv('data.csv', index=False)
        # csv_path = os.path.join("outputs", "data.csv")
        csv_path = "data.csv"
        state["text2sql_results"] = {"query": query,
                                          "csv_path": csv_path
                                          }
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    
class TextToSQL(BaseModel):
    sql_query: str = Field(description="the sql query to be executed")
    
if __name__ == "__main__":
    c = Node()
    print(c())
