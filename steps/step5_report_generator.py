from typing import Any
from utils import State


class Node:
    def __init__(self) -> None:
        pass

    def forward(self, state: State):
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    


if __name__ == "__main__":
    c = Node()
    print(c())
