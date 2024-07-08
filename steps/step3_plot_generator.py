from typing import Any
from utils import AgentState, LLM
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from logging_config import LoggerManager, LogState
from matplotlib import pyplot as plt
from glob import glob
import os
import re

class PlotGeneratorNode:
    def __init__(self) -> None:
        self.llm = LLM("togetherAI")
        # self.llm = LLM("openAI")
        # self.llm = LLM("cluade")

    def forward(self, state: AgentState):
        LoggerManager.log_flow(f"Start with {self.llm.model_name}", node=self.__class__.__name__, state=LogState.START)
        try:
            csv_file = state["text2sql_results"]["csv_path"]
            user_query = state["question"]
            hypothesis = state["data_analytics_results"]["hypothesis"]
            csv_summery = state["data_analytics_results"]["summary_text"]
            plot_generator_results = {}
            df = pd.read_csv(csv_file)
            num_rows = len(df)
            columns = df.columns.tolist()
            columns_text = "The CSV file Columns are: " + ", ".join(columns)
            LoggerManager.log_flow(f"CSV file loaded with {num_rows} rows and columns: {columns}", node=self.__class__.__name__)

            #Tha main scenario is when the CSV file has more than one row
            if num_rows > 1:
                parser = JsonOutputParser(pydantic_object=TextAndCode)

                prompt = PromptTemplate(
                    template="Answer the user query.\n{format_instructions}\n{user_prompt}\n{hypothesis}\n{csv_summery}",
                    input_variables=["user_prompt", "hypothesis", "csv_summery"],
                    partial_variables={"format_instructions": parser.get_format_instructions()},
                )

                chain = prompt | self.llm | parser

                result = chain.invoke({"user_prompt": user_query, "hypothesis":hypothesis,"csv_summery": csv_summery})
                plot_generator_results["answer"] = result["intro"]
                plot_generator_results["plot_code"] = result["code"]
                LoggerManager.log_flow(f"Plot code generated:\n```python\n{result['code']}\n```", node=self.__class__.__name__, state=LogState.RESPONSE)
            
            #The edge case is when the CSV file has only one row
            else:
                output_parser = StrOutputParser()
                row = df.to_dict(orient='records')[0]
                firstRow_text = "Row data: " + ", ".join([f"{col}: {row[col]}" for col in columns]) + "\n"
                prompt = PromptTemplate(
                    template="Answer the user query based on the retrived information.\n{format_instructions}\n{user_prompt}\n{columns_text}\n{firstRow_text}",
                    input_variables=["user_prompt", "columns_text", "firstRow_text"],
                    partial_variables={"format_instructions": output_parser.get_format_instructions()},
                )
                chain = prompt | self.llm | output_parser
                result = chain.invoke({"user_prompt": user_query, "columns_text": columns_text, "firstRow_text": firstRow_text})
                plot_generator_results["answer"] = result[0]
                LoggerManager.log_flow(f"Answer generated for single row data:\n{result[0]}", node=self.__class__.__name__, state=LogState.RESPONSE)
                
            LoggerManager.log_flow(f"State updated with plot generator results:\n{plot_generator_results}", node=self.__class__.__name__)

            LoggerManager.log_flow(f"Started", node='PlotCode', state=LogState.START)
            code = plot_generator_results["plot_code"]
            code = re.sub(r"plt\.show\(\)", "", code)
            plt.switch_backend('Agg')
            exec(code)
            plot_id = len(glob("static/plot_*.png"))
            plot_filename = os.path.join("static", f"plot_{plot_id}.png")
            plt.savefig(plot_filename)
            plt.close()
            plot_generator_results["plot_filename"] = plot_filename
            state["plot_generator_results"] = plot_generator_results

            LoggerManager.log_flow(f"Save plot in: {plot_filename}", node='PlotCode', state=LogState.FINISH)
        except:
            LoggerManager.log_flow_metric(node='PlotCode', state=LogState.ERROR)
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    
# Define your desired data structure.
class TextAndCode(BaseModel):
    intro: str = Field(description="Short explanation and answer to user prompt to put as plot image header")
    code: str = Field(description="Python code to generate one plot from the CSV file in 'data.csv' to answer the user query")
    
if __name__ == "__main__":
    c = PlotGeneratorNode()
    print(c())
