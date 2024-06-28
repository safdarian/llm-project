from langgraph.graph import StateGraph, END
from utils import AgentState, ConfigManager
from steps.step1_text2sql import Node as Node1
from steps.step2_data_analytics import Node as Node2
from steps.step3_plot_generator import Node as Node3
from steps.step4_data_storytelling import Node as Node4
from steps.step5_report_generator import Node as Node5
from steps.fallback_node import Node as FallbackNode
from steps.router_node import Node as RouterNode

import logging
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class ModelStateManager:
    def __init__(self) -> None:
        self.create_graph()

    def create_graph(self):
        self.step1 = Node1()
        self.step2 = Node2()
        self.step3 = Node3()
        self.step4 = Node4()
        self.step5 = Node5()
        self.fallback = FallbackNode()
        self.router = RouterNode()
        
        self.graph = StateGraph(AgentState)
        self.graph.add_node("text2sql", self.step1)
        self.graph.add_node("analytics", self.step2)
        self.graph.add_node("plot", self.step3)
        self.graph.add_node("story", self.step4)
        self.graph.add_node("report", self.step5)
        self.graph.add_node("fallback", self.fallback)
        
        self.graph.set_conditional_entry_point(
            self.router,
            {
                "LLMFallback": "fallback",
                "Text2SQL": "text2sql",
            },
        )

        self.graph.add_edge("text2sql", "analytics")
        self.graph.add_edge("analytics", "plot")
        self.graph.add_edge("plot", "story")
        self.graph.add_edge("story", "report")
        self.graph.add_edge("report", END)
        self.graph.add_edge("fallback", END)
        self.compiled_graph = self.graph.compile()

    def execute(self, question):
        return self.compiled_graph.invoke({"question": question})


if __name__ == "__main__":
    config = ConfigManager()
    question = "What is the total sales amount for each product?"
    sm = ModelStateManager()
    result = sm.execute(question=question)
    logger.info(f"Whole State:\n{result}" + ("-" * 50))
    logger.info(f"Text-to-SQL Results:\n"+result["text2sql_results"] + "\n" + ("-" * 50))
    logger.info(f"Plot Generator Results:\n"+result["plot_generator_results"])