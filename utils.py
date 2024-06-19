from langgraph.graph import StateGraph, END
from typing_extensions import Annotated, TypedDict
from langchain_core.runnables import RunnableConfig


class State(TypedDict):
     question: str
     db_schema: dict
     text_2_sql_results: dict
     data_analytics_results: dict
     plot_generator_results: dict
     data_storytelling_results: dict
     report_generation_results: dict
     
