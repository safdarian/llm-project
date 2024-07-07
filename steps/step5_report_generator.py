from typing import Any
from utils import AgentState
from matplotlib import pyplot as plt
import os
from glob import glob
import re
from logging_config import LoggerManager, LogState

class ReportGenerationNode:
    def __init__(self) -> None:
        pass

    def forward(self, state: AgentState):
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    


if __name__ == "__main__":
    c = ReportGenerationNode()
    print(c())
