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
        if state.get("data_analytics_results"):
            if state.get("data_analytics_results").get("error"):
                ans = "error"
                desc = state.get("data_analytics_results").get("error_description")
                fallback_type = "hint"
            else:
                ans = "confirm"
                desc = state.get("data_analytics_results").get("summary_text") + " - " + state.get("data_analytics_results").get("hypothesis")
                fallback_type = "confirm"
        if state["fallback_info"]["fallbacks"][2] > 0:
            state["fallback_info"]["confirm_premessage"] = "Summary Text + Hypothesis"
            state["fallback_info"]["fallback_desc"] = desc
            ans = "fallback"
        else:
            ans = "go"
        return ans
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)

