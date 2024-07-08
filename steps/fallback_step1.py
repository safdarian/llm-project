from typing import Any
from utils import AgentState, ConfigManager, LLM
from db_manager import DBManager
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from logging_config import LoggerManager, LogState

class FallBackNode:
    def __init__(self) -> None:
        self.config = ConfigManager()
        # self.llm = LLM("togetherAI")
        # self.llm = LLM("openAI")
        # self.llm = LLM("cluade")

    def forward(self, state: AgentState):
        # LoggerManager.log_flow(f"Start with {self.llm.model_name}", node=self.__class__.__name__, state=LogState.START)
        if state.get("text2sql_results"):
            if state.get("text2sql_results").get("error"):
                ans = "error"
                desc = state.get("text2sql_results").get("error_description")
                fallback_type = "hint"
            else:
                ans = "confirm"
                desc = state.get("text2sql_results").get("query")
                fallback_type = "confirm"
        if state["fallback_info"]["fallbacks"][1] > 0:
            state["fallback_info"]["confirm_premessage"] = "Generated SQL Query:"
            state["fallback_info"]["fallback_desc"] = desc
            ans = "fallback"
        else:
            ans = "go"
        return ans
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)

