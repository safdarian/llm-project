from typing import Any
from utils import AgentState


class DataStorytellingNode:
    def __init__(self) -> None:
        pass

    def forward(self, state: AgentState):
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    


if __name__ == "__main__":
    c = DataStorytellingNode()
    print(c())
