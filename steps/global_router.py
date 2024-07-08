from typing import Any
from utils import AgentState, ConfigManager, LLM
from db_manager import DBManager
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from logging_config import LoggerManager, LogState
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json


class GlobalRouter:
    def __init__(self) -> None:
        self.config = ConfigManager()
        # self.llm = LLM("togetherAI")
        # self.llm = LLM("openAI")
        # self.llm = LLM("cluade")

    def forward(self, state: AgentState):
        
        fallback2states = {
            0: "node0",
            1: "text2sql",
            2: "analytics",
            3: "plot",
            4: "story"
        }
        ans = fallback2states[state["fallback_info"]["current_state"]]
        return ans
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
