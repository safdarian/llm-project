from typing import Any
from utils import State, ConfigManager, LLM
from langchain_together import Together
import re
import os
from db_manager import DBManager
import pandas as pd

class Node:
    def __init__(self) -> None:
        self.config = ConfigManager()
        self.db = DBManager(self.config["database"])
        self.llm = LLM("togetherAI")
    def forward(self, state: State):
        question = state.get("question")
        template = """according to this database schema:
        {}
        give me a query to answer this question:
        {}
        put answer in this format:
        ```sql query```"""
        
        answer = self.llm(template.format(self.db.get_schema(), question))
        if len(re.findall(r"```sql(.*)```", answer, re.DOTALL)) > 0:
            query = re.findall(r"```sql(.*?)```", answer, re.DOTALL)[0].strip()
        
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
    

if __name__ == "__main__":
    c = Node()
    print(c())
