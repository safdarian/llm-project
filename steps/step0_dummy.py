from typing import Any
from utils import AgentState, ConfigManager, LLM
from db_manager import DBManager
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from logging_config import LoggerManager, LogState

class Step0_DummyNode:
    def __init__(self) -> None:
        pass

    def forward(self, state: AgentState):
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    
if __name__ == "__main__":
    c = Text2SQLNode()
    print(c())
