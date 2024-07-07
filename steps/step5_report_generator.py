from typing import Any
from utils import AgentState
from matplotlib import pyplot as plt
import os
from glob import glob
import re
from logging_config import LoggerManager, LogState
from utils import AgentState, LLM

class ReportGenerationNode:
    def __init__(self) -> None:
        self.llm = LLM("openAI")

    def forward(self, state: AgentState):
        LoggerManager.log_flow(f"Start with {self.llm.model_name}", node=self.__class__.__name__, state=LogState.START)
        LoggerManager.log_flow_metric(node=self.__class__.__name__, state=LogState.RESPONSE)
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    


if __name__ == "__main__":
    c = ReportGenerationNode()
    print(c())
