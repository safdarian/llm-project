from langgraph.graph import StateGraph, END
from typing_extensions import Annotated, TypedDict
from langchain_core.runnables import RunnableConfig
from utils import State
from steps.step1_text2sql import Node as Node1
from steps.step2_data_analytics import Node as Node2
from steps.step3_plot_generator import Node as Node3
from steps.step4_data_storytelling import Node as Node4
from steps.step5_report_generator import Node as Node5


class ModelStateManager:
    def __init__(self, db_info) -> None:
        self.db_info = db_info
        self.step1 = Node1(self.db_info)
        self.step2 = Node2()
        self.step3 = Node3()
        self.step4 = Node4()
        self.step5 = Node5()
        
        self.graph = StateGraph(State)
        self.graph.add_node("text2sql", self.step1.forward)
        self.graph.add_node("analytics", self.step2.forward)
        self.graph.add_node("plot", self.step3.forward)
        self.graph.add_node("story", self.step4.forward)
        self.graph.add_node("report", self.step5.forward)
        self.graph.set_entry_point("text2sql")

        self.graph.add_edge("text2sql", "analytics")
        self.graph.add_edge("analytics", "plot")
        self.graph.add_edge("plot", "story")
        self.graph.add_edge("story", "report")
        self.compiled_graph = self.graph.compile()

    def execute(self, question):
        return self.compiled_graph.invoke({"question": question})


if __name__ == "__main__":
    sm = ModelStateManager(db_info="ok")
    print(sm.execute(question="hello"))