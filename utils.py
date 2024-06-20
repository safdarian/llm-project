from langgraph.graph import StateGraph, END
from typing_extensions import Annotated, TypedDict
from langchain_core.runnables import RunnableConfig
import json
from langchain_together import Together
from typing import Any



class State(TypedDict):
     question: str
     db_data: dict
     text2sql_results: dict
     data_analytics_results: dict
     plot_generator_results: dict
     data_storytelling_results: dict
     report_generation_results: dict
     
class ConfigManager(dict):
    def __init__(self) -> None:
        super().__init__()
        with open("configs.json") as f:
            self.update(json.loads(f.read()))
    

class LLM:
    def __init__(self, llm_source="togetherAI", additional_config={}) -> None:
        self.config = ConfigManager()
        self.additional_config = additional_config
        llm_init_map = {
            "togetherAI": self.init_togetherAI
        }
        llm_forward_map = {
            "togetherAI": self.forward_togetherAI
        }
        self.llm_init = llm_init_map[llm_source]
        self.llm_forward = llm_forward_map[llm_source]
        self.llm_init()
    
    def init_togetherAI(self):
        self.llm = Together(model="meta-llama/Llama-3-8b-chat-hf", together_api_key=self.config["togetherAI"])
    
    def forward_togetherAI(self, prompt):
        return self.llm.invoke(prompt)
    
    def forward(self, prompt):
        return self.llm_forward(prompt=prompt)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
