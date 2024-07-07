from typing import Any
from utils import AgentState, LLM
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from logging_config import LoggerManager, LogState

class PlotGeneratorNode:
    def __init__(self) -> None:
        self.llm = LLM("togetherAI")
        # self.llm = LLM("openAI")
        # self.llm = LLM("cluade")

    def forward(self, state: AgentState):
        LoggerManager.log_flow(f"Start with {self.llm.model_name}", node=self.__class__.__name__, state=LogState.START)
        csv_file = state["text2sql_results"]["csv_path"]
        user_query = state["question"]
        plot_generator_results = {}
        df = pd.read_csv(csv_file)
        num_rows = len(df)
        columns = df.columns.tolist()
        columns_text = "The CSV file Columns are: " + ", ".join(columns)
        LoggerManager.log_flow(f"CSV file loaded with {num_rows} rows and columns: {columns}", node=self.__class__.__name__)

        if num_rows > 1:
            parser = JsonOutputParser(pydantic_object=TextAndCode)

            prompt = PromptTemplate(
                template="Answer the user query.\n{format_instructions}\n{user_prompt}\n{columns_text}",
                input_variables=["user_prompt", "columns_text"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            chain = prompt | self.llm | parser

            result = chain.invoke({"user_prompt": user_query, "columns_text": columns_text})
            plot_generator_results["answer"] = result["intro"]
            plot_generator_results["plot_code"] = result["code"]
            LoggerManager.log_flow(f"Plot code generated:\n```python\n{result['code']}\n```", node=self.__class__.__name__, state=LogState.RESPONSE)
        else:
            output_parser = StrOutputParser()
            row = df.to_dict(orient='records')[0]
            firstRow_text = "Row data: " + ", ".join([f"{col}: {row[col]}" for col in columns]) + "\n"
            prompt = PromptTemplate(
                template="Answer the user query.\n{format_instructions}\n{user_prompt}\n{columns_text}\n{firstRow_text}",
                input_variables=["user_prompt", "columns_text", "firstRow_text"],
                partial_variables={"format_instructions": output_parser.get_format_instructions()},
            )
            chain = prompt | self.llm | output_parser
            result = chain.invoke({"user_prompt": user_query, "columns_text": columns_text, "firstRow_text": firstRow_text})
            plot_generator_results["answer"] = result[0]
            LoggerManager.log_flow(f"Answer generated for single row data:\n{result[0]}", node=self.__class__.__name__, state=LogState.RESPONSE)
        state["plot_generator_results"] = plot_generator_results
        LoggerManager.log_flow(f"State updated with plot generator results:\n{plot_generator_results}", node=self.__class__.__name__)
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    
# Define your desired data structure.
class TextAndCode(BaseModel):
    intro: str = Field(description="Short rephrased explanation and answer to user prompt to put as plot image header")
    code: str = Field(description="Python code to generate one plot from the CSV file in 'data.csv' to answer the user query")
    
if __name__ == "__main__":
    c = PlotGeneratorNode()
    print(c())
