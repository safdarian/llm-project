from langgraph.graph import StateGraph, END, START
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
from steps.global_router import GlobalRouter
from steps.fallback_step1 import FallBackNode as node1_fallback
from steps.fallback_step2 import FallBackNode as node2_fallback
from steps.fallback_step3 import FallBackNode as node3_fallback
from steps.fallback_step4 import FallBackNode as node4_fallback

class ModelStateManager:
    def __init__(self) -> None:
        self.create_graph()

    def create_graph(self):
        self.global_router = GlobalRouter()

        self.step1_fallback = node1_fallback()
        self.step2_fallback = node2_fallback()
        self.step3_fallback = node3_fallback()
        self.step4_fallback = node4_fallback()

        self.step0 = Node0_Dummy()
        self.step0_router = Node0_Router()
        self.direct_llm = Node0_DirectLLM()

        self.router = RouterNode()
        self.step1 = Node1()
        self.step2 = Node2()
        self.step3 = Node3()
        self.step4 = Node4()
        
        self.graph = StateGraph(AgentState)
        self.graph.add_node("question_filter", self.step0)
        self.graph.add_node("direct_llm", self.direct_llm)
        self.graph.add_node("text2sql", self.step1)
        self.graph.add_node("analytics", self.step2)
        self.graph.add_node("plot", self.step3)
        self.graph.add_node("story", self.step4)
        # self.graph.add_node("fallback", self.fallback)
        # self.graph.set_entry_point("text2sql")
        # self.graph.set_entry_point("question_filter")
        # self.graph.set_conditional_entry_point(
        #     self.router,
        #     {
        #         "LLMFallback": "fallback",
        #         "Text2SQL": "text2sql",
        #     },
        # )

        # self.graph.add_edge("text2sql", "analytics")
        self.graph.add_conditional_edges("text2sql", self.step1_fallback, {
                                 "go": "analytics",
                                 "fallback": END 
                            })
        # self.graph.add_edge("analytics", "plot")
        self.graph.add_conditional_edges("analytics", self.step2_fallback, {
                                 "go": "plot",
                                 "fallback": END 
                            })
        
        # self.graph.add_edge("plot", "story")
        self.graph.add_conditional_edges("plot", self.step3_fallback, {
                                 "go": "story",
                                 "fallback": END 
                            })
        
        # self.graph.add_edge("story", END)
        self.graph.add_conditional_edges("story", self.step4_fallback, {
                                 "go": END,
                                 "fallback": END 
                            })
        
        self.graph.add_edge("direct_llm", END)
        self.graph.add_conditional_edges(START, self.global_router, {
                                 "node0": "question_filter",
                                 "text2sql": "text2sql",
                                 "analytics": "analytics",
                                 "plot": "plot",
                                 "story": "story"
                            })
        self.graph.add_conditional_edges("question_filter", 
                            self.step0_router, {
                                 "LLMFallback": "direct_llm",
                                 "Text2SQL": "text2sql" 
                            })
        # self.graph.add_conditional_edges("text2sql_fallback", )
        # self.graph.add_edge("fallback", END)
        self.compiled_graph = self.graph.compile()
    def save_graph_image(self):
        plot = self.compiled_graph.get_graph().draw_mermaid_png()
        with open("plot.png", "wb") as fp:
            fp.write(plot)
    
    def execute(self, state, fallback_info=None):
        state["fallback_info"] = fallback_info
        return self.compiled_graph.invoke(state)


if __name__ == "__main__":
    config = ConfigManager()
    question = "Hello How Are you?"
    # question = "What is the total sales amount for each product?"
    sm = ModelStateManager()
    sm.save_graph_image()
    # result = sm.execute(question=question)
    # print("Whole State:", result, ("-" * 50))
    # print("Text-to-SQL Results:", result["text2sql_results"], ("-" * 50))
    # print("Plot Generator Results:", result["plot_generator_results"], "-" * 50)
