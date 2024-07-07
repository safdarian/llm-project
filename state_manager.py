from langgraph.graph import StateGraph, END
from utils import AgentState, ConfigManager
from steps.step0_question_filter_router import RouterNode as Node0_Router
from steps.step0_question_filter import DirectQuestionNode as Node0_DirectLLM
from steps.step0_dummy import Step0_DummyNode as Node0_Dummy
from steps.step1_text2sql import Text2SQLNode as Node1
from steps.step2_data_analytics import DataAnalyticsNode as Node2
from steps.step3_plot_generator import PlotGeneratorNode as Node3
from steps.step4_data_storytelling import DataStorytellingNode as Node4
from steps.fallback import FallBackNode
from steps.router_node import RouterNode as RouterNode

class ModelStateManager:
    def __init__(self) -> None:
        self.create_graph()

    def create_graph(self):
        self.step0 = Node0_Dummy()
        self.direct_llm = Node0_DirectLLM()
        self.step0_router = Node0_Router()
        self.step1 = Node1()
        self.step2 = Node2()
        self.step3 = Node3()
        self.step4 = Node4()
        self.router = RouterNode()
        
        self.graph = StateGraph(AgentState)
        self.graph.add_node("question_filter", self.step0)
        self.graph.add_node("direct_llm", self.direct_llm)
        self.graph.add_node("text2sql", self.step1)
        self.graph.add_node("analytics", self.step2)
        self.graph.add_node("plot", self.step3)
        self.graph.add_node("story", self.step4)
        # self.graph.add_node("fallback", self.fallback)
        # self.graph.set_entry_point("text2sql")
        self.graph.set_entry_point("question_filter")
        # self.graph.set_conditional_entry_point(
        #     self.router,
        #     {
        #         "LLMFallback": "fallback",
        #         "Text2SQL": "text2sql",
        #     },
        # )

        self.graph.add_edge("text2sql", "analytics")
        self.graph.add_edge("analytics", "plot")
        self.graph.add_edge("plot", "story")
        self.graph.add_edge("story", END)
        self.graph.add_edge("direct_llm", END)
        self.graph.add_conditional_edges("question_filter", 
                            self.step0_router, {
                                 "LLMFallback": "direct_llm",
                                 "Text2SQL": "text2sql" 
                            })
        # self.graph.add_conditional_edges("text2sql_fallback", )
        # self.graph.add_edge("fallback", END)
        self.compiled_graph = self.graph.compile()

    def execute(self, question):
        return self.compiled_graph.invoke({"question": question})


if __name__ == "__main__":
    config = ConfigManager()
    question = "Hello How Are you?"
    # question = "What is the total sales amount for each product?"
    sm = ModelStateManager()
    result = sm.execute(question=question)
    print("Whole State:", result, ("-" * 50))
    print("Text-to-SQL Results:", result["text2sql_results"], ("-" * 50))
    print("Plot Generator Results:", result["plot_generator_results"], "-" * 50)
