from typing import Any
from utils import State, LLM
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_together import Together
import pandas as pd
from langchain_core.output_parsers import StrOutputParser




class Node:
    def __init__(self) -> None:
        self.llm = LLM(llm_source="togetherAI", additional_config={"model": "meta-llama/Llama-3-8b-chat-hf"})
        pass

    def forward(self, state: State):
        print(state)
        csv_file = state["text2sql_results"]["csv_path"]
        user_query = state["question"]
        plot_generator_results = {}
        df = pd.read_csv(csv_file)
        num_rows = len(df)
        columns = df.columns.tolist()
        columns_text = "The CSV file Columns are: " + ", ".join(columns)
        if num_rows > 1:
            #instruct_prompt = "Generate a python code so it plots the user query based on the given csv file columns."

            parser = JsonOutputParser(pydantic_object=TextAndCode)

            prompt = PromptTemplate(
                template="Answer the user query.\n{format_instructions}\n{user_prompt}\n{columns_text}",
                input_variables=["user_prompt" ,"columns_text"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            chain = prompt | self.llm.get_langchain_model() | parser

            result = chain.invoke({"user_prompt": user_query, "columns_text": columns_text})
            plot_generator_results["answer"] = result["intro"]
            #print("----------------------------------")
            #print("The inrto:",state["intro"])
            plot_generator_results["plot_code"] = result["code"]
            #print("The code:",state["plot_code"])
            #print("----------------------------------")
        else:
            #instruct_prompt = ""
            output_parser = StrOutputParser()
            row = df.to_dict(orient='records')
            firstRow_text += "Row data: " + ", ".join([str(row[col]) for col in columns]) + "\n"
            prompt = PromptTemplate(
                template="Answer the user query.\n{format_instructions}\n{user_prompt}\n{columns_text}\n{firstRow_text}",
                input_variables=["user_prompt" ,"columns_text","firstRow_text"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )
            chain = prompt | self.llm.get_langchain_model() | output_parser
            result = chain.invoke({"user_prompt": user_query, "columns_text": columns_text, "firstRow_text": firstRow_text})
            plot_generator_results["answer"] = result[0]
        state["plot_generator_results"] = plot_generator_results
        #print(state)
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    
# Define your desired data structure.
class TextAndCode(BaseModel):
    intro: str = Field(description="intro about the user query answer")
    code: str = Field(description="code to generate one plot from the CSV file in 'csv_path' to answer the user query ")
    
if __name__ == "__main__":
    c = Node()
    print(c())
