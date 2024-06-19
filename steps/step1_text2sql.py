from typing import Any
from utils import State, ConfigManager
from langchain_together import Together
import copy
import re


class Node:
    def __init__(self, db_info) -> None:
        self.config = ConfigManager()
        self.db_info = db_info
        self.llm = Together(model="meta-llama/Llama-3-8b-chat-hf", together_api_key=self.config["togetherAI"])
    def forward(self, input_data: State):
        question = input_data.get("question")
        template = """according to this database schema:
        {}
        give me a query to answer this question:
        {}
        put answer in this format:
        ```sql query```"""
        
        answer = self.llm.invoke(template.format(self.db_info["schema"], question))
        if len(re.findall(r"```sql(.*)```", answer, re.DOTALL)) > 0:
            answer = re.findall(r"```sql(.*?)```", answer, re.DOTALL)[0].strip()
        ans_dict = copy.copy(input_data)
        ans_dict["text2sql_results"] = answer
        return ans_dict
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    

if __name__ == "__main__":
    c = Node()
    print(c())
