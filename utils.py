from langgraph.graph import StateGraph, END
from typing_extensions import Annotated, TypedDict
from langchain_core.runnables import RunnableConfig
import json

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
    
    