from typing import Any
from utils import State, ConfigManager, LLM
from langchain_together import Together
import re
import os


class Node:
    def __init__(self, db_info) -> None:
        self.config = ConfigManager()
        self.db_info = db_info
        self.llm = LLM("togetherAI")
    def forward(self, state: State):
        question = state.get("question")
        template = """according to this database schema:
        {}
        give me a query to answer this question:
        {}
        put answer in this format:
        ```sql query```"""
        
        answer = self.llm(template.format(self.db_info["schema"], question))
        if len(re.findall(r"```sql(.*)```", answer, re.DOTALL)) > 0:
            answer = re.findall(r"```sql(.*?)```", answer, re.DOTALL)[0].strip()
        # ans_dict = copy.copy(state)
        csv_path = os.path.join("outputs", "business_sales_data_updated.csv")
        state["text2sql_results"] = {"query": answer,
                                          "csv_path": csv_path
                                          }
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    

if __name__ == "__main__":
    c = Node()
    print(c())
