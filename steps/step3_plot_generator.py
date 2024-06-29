from typing import Any
from utils import AgentState, LLM
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from langchain_core.output_parsers import StrOutputParser
import logging
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class Node:
    def __init__(self) -> None:
        self.llm = LLM("togetherAI")
        # self.llm = LLM("openAI")
        # self.llm = LLM("cluade")
        logger.info("Node3 (Plot-Generator) initialized")

    def forward(self, state: AgentState):
        logger.info("Forward method called with state: %s", state)
        csv_file = state["text2sql_results"]["csv_path"]
        user_query = state["question"]
        plot_generator_results = {}
        df = pd.read_csv(csv_file)
        num_rows = len(df)
        columns = df.columns.tolist()
        columns_text = "The CSV file Columns are: " + ", ".join(columns)
        logger.info("CSV file loaded with %d rows and columns: %s", num_rows, columns)

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
            logger.info("Plot code generated:\n%s", result["code"])
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
            logger.info("Answer generated for single row data:\n%s", result[0])
        state["plot_generator_results"] = plot_generator_results
        logger.info("State updated with plot generator results:\n%s", plot_generator_results)
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    
# Define your desired data structure.
class TextAndCode(BaseModel):
    intro: str = Field(description="Short rephrased explanation and answer to user prompt to put as plot image header")
    code: str = Field(description="Python code to generate one plot from the CSV file in 'data.csv' to answer the user query")
    
if __name__ == "__main__":
    c = Node()
    print(c())
