from langgraph.graph import StateGraph, END
from typing_extensions import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
import json
from langchain_together import Together, ChatTogether
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
        self.llm_source = llm_source
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
        self.model_name = self.additional_config.get("model", "meta-llama/Llama-3-8b-chat-hf")
        self.llm = Together(model=self.model_name, together_api_key=self.config["togetherAI"])
    
    def forward_togetherAI(self, prompt):
        return self.llm.invoke(prompt)
    

    def get_langchain_model(self):
        if self.llm_source == "togetherAI":
            return ChatTogether(model=self.model_name, together_api_key=self.config["togetherAI"])

    def forward(self, prompt):
        return self.llm_forward(prompt=prompt)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
