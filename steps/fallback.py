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
    def __init__(self, last_node, last_node_results) -> None:
        self.config = ConfigManager()
        self.last_node = last_node
        self.last_node_results = last_node_results
        self.llm = LLM("togetherAI")
        # self.llm = LLM("openAI")
        # self.llm = LLM("cluade")

    def forward(self, state: AgentState):
        LoggerManager.log_flow(f"Start with {self.llm.model_name}", node=self.__class__.__name__, state=LogState.START)
        if state.get(self.last_node_results):
            if state.get(self.last_node_results).get("error"):
                ans = "error"
                desc = state.get(self.last_node_results).get("error_description")
                fallback_type = "hint"
            else:
                ans = "confirm"
                desc = state.get(self.last_node_results).get("confirm_description")
                fallback_type = "confirm"
        
        state["fallback_info"]["last_executed_state"] = self.last_node
        if state["fallback_info"]["num_fallbacks"] == 0:
            state["fallback_info"]["fallback"] = True
            state["fallback_info"]["num_fallbacks"] += 1
            state["fallback_info"]["fallback_type"] = fallback_type
            state["fallback_info"]["fallback_desc"] = desc
            ans = "fallback"
        else:
            state["fallback_info"] = {
                "last_executed_state": self.last_node,
                "num_fallbacks": 0,
                "fallback": False,
                "fallback_type": None,
                "fallback_desc": None,
                "fallback_confirm_response": None,
                "fallback_error_response": None
            }
            ans = "go"
        # LoggerManager.log_flow("State updated with text2sql results: %s", state["text2sql_results"])
        return ans
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)

