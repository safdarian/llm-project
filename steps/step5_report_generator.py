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
        LoggerManager.log_flow(f"Started", node=self.__class__.__name__, state=LogState.START)
        code = state["plot_generator_results"]["plot_code"]
        code = re.sub(r"plt\.show\(\)", "", code)
        plt.switch_backend('Agg')
        exec(code)
        plot_id = len(glob("static/plot_*.png"))
        plot_filename = os.path.join("static", f"plot_{plot_id}.png")
        plt.savefig(plot_filename)
        plt.close()
        state["report_generation_results"] = {
            "plot_filename": plot_filename
            }
        LoggerManager.log_flow(f"Save plot in: {plot_filename}", node=self.__class__.__name__, state=LogState.FINISH)
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    


if __name__ == "__main__":
    c = ReportGenerationNode()
    print(c())
