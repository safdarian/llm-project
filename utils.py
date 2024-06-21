from langgraph.graph import StateGraph, END
from typing_extensions import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
import json
from langchain_together import Together, ChatTogether
from typing import Any
from langchain_openai import ChatOpenAI



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
            "togetherAI": self.init_togetherAI,
            "localMLX": self.init_localMLX,
            "openAI": self.init_openAI
        }
        self.llm_init = llm_init_map[llm_source]
        self.llm_init()
    
    def init_togetherAI(self):
        self.model_name = self.additional_config.get("model", "meta-llama/Llama-3-8b-chat-hf")
        self.llm = ChatTogether(model=self.model_name, together_api_key=self.config["api"]["togetherAI"])
    
    def init_localMLX(self): 
        from langchain_community.llms.mlx_pipeline import MLXPipeline
        from langchain_community.chat_models.mlx import ChatMLX
        #self.model_name = MLXPipeline.from_model_id("mlx-community/Meta-Llama-3-8B-Instruct-4bit")
        self.model_name = MLXPipeline.from_model_id("mlx-community/Meta-Llama-3-8B-Instruct-8bit",pipeline_kwargs={"max_tokens": 256, "temp": 0.1},)
        self.llm = ChatMLX(llm=self.model_name)
    
    def init_openAI(self):
        #self.model_name = self.additional_config.get("model", "gpt-4o")
        self.model_name = "gpt-4o"
        
        self.llm = ChatOpenAI(
        model=self.model_name,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=self.config["api"]["openAI"],
        )

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.llm
