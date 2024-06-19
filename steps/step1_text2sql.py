from typing import Any
from utils import State


class Node:
    def __init__(self, db_info) -> None:
        self.db_info = db_info

    def forward(self, input_data: State):
        return input_data
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    


if __name__ == "__main__":
    c = Node()
    print(c())
