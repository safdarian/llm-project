from typing import Any
from utils import AgentState, ConfigManager, LLM
from db_manager import DBManager
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from logging_config import LoggerManager, LogState
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json


class Text2SQLNode:
    def __init__(self) -> None:
        self.config = ConfigManager()
        self.db = DBManager(self.config["database"])
        #self.llm = LLM("togetherAI")
        self.llm = LLM("openAI")
        # self.llm = LLM("cluade")
        self.examples = self.load_examples(os.path.join("helper_data","text2sql_examples.json"))
        self.tfidf_vectorizer, self.tfidf_matrix = self.setup_tfidf(self.examples)
    
    def load_examples(self, filepath: str) -> pd.DataFrame:
        with open(filepath, 'r') as file:
            examples = json.load(file)
        return pd.DataFrame(examples)
    
    def setup_tfidf(self, examples: pd.DataFrame):
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(examples['question'])
        return vectorizer, tfidf_matrix
    
    def tfidf_retriever(self, query: str, top_k: int = 3):
        query_vec = self.tfidf_vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        ranked_indices = scores.argsort()[::-1][:top_k]
        return self.examples.iloc[ranked_indices].to_dict('records')
    
    def format_retrieved_examples(self, retrieved_examples) -> str:
        formatted_examples = ""
        for example in retrieved_examples:
            formatted_examples += f"Question: {example['question']}\n"
            formatted_examples += f"Evidence: {example['evidence']}\n"
            formatted_examples += f"SQL: {example['SQL']}\n\n"
        return formatted_examples

    def step_back_prompting(self, question):
        parser = JsonOutputParser(pydantic_object=StepBackPrompt)
        prompt = PromptTemplate(
            template=  "Answer the user query.\n{format_instructions}\n{user_prompt}\nThe Database schema of Tables and their first row values are: {db_schema}",
            input_variables=["user_prompt" ,"db_schema"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.llm | parser
        step_back = chain.invoke({"user_prompt": question, "db_schema": self.db.get_db_head()})
        return step_back["step_back_question"]

    def forward(self, state: AgentState):
        LoggerManager.log_flow(f"Start with {self.llm.model_name}", node=self.__class__.__name__, state=LogState.START)
        queries = []
        queries_dict = {}
        
        # Question
        question = state.get("question")

        if state.get("fallback_info"):
            if state["fallback_info"].get("fallback_confirm_response"):
                question += " {}".format(state["fallback_info"]["fallback_confirm_response"])
        LoggerManager.log_flow(question)
        parser = JsonOutputParser(pydantic_object=TextToSQL)
        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\nThe User initial prompt: {user_prompt}\nThe Database schema of Tables and their first row values are: {db_schema}",
            input_variables=["user_prompt" ,"db_schema"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.llm | parser
        answer = chain.invoke({"user_prompt": question, "db_schema": self.db.get_db_head()})
        query = answer["sql_query"]
        queries.append(query)
        queries_dict["Question"] = query

        # Step Back
        step_back_question = self.step_back_prompting(question)
        parser = JsonOutputParser(pydantic_object=TextToSQL)
        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\nThe User initial prompt: {user_prompt}\nThe Database schema of Tables and their first row values are: {db_schema}",
            input_variables=["user_prompt" ,"db_schema"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.llm | parser
        answer = chain.invoke({"user_prompt": step_back_question, "db_schema": self.db.get_db_head()})
        query = answer["sql_query"]
        queries.append(query)
        queries_dict["StepBack"] = query

        # RAG
        retrieved_examples = self.tfidf_retriever(question)
        formatted_examples = self.format_retrieved_examples(retrieved_examples)
        prompt = PromptTemplate(
            template="Answer the user query using the few-shot examples provided.\n{format_instructions}\n{examples}\nUser Question: {user_prompt}\nThe Database schema of Tables and their first row values are: {db_schema}",
            input_variables=["user_prompt", "db_schema", "examples"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.llm | parser
        answer = chain.invoke({"user_prompt": step_back_question, "db_schema": self.db.get_db_head(), "examples": formatted_examples})
        query = answer["sql_query"]
        queries.append(query)
        queries_dict["RAG"] = query
        orders = ["Question", "StepBack", "RAG"]
        priorities = ["StepBack", "RAG", "Question"]
        
        LoggerManager.log_flow(f"SQL query generated: \"{query}\"", node=self.__class__.__name__, state=LogState.RESPONSE)
        results = []
        for query, order in zip(queries, orders):
            try:
                current_result = self.db.query(query)
            except Exception:
                current_result = []
            results.append((current_result, order))
            
        results = sorted(results, key=lambda x: len(x[0]))

        df = pd.DataFrame(results[-1][0])
        df.to_csv('data.csv', index=False)
        # csv_path = os.path.join("outputs", "data.csv")
        csv_path = "data.csv"
        
        state["text2sql_results"] = {"query": query, "csv_path": csv_path}
        # LoggerManager.log_flow("State updated with text2sql results: %s", state["text2sql_results"])
        return state
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)
    
class TextToSQL(BaseModel):
    sql_query: str = Field(description="the sql query to be executed")

class StepBackPrompt(BaseModel):
    explanation: str = Field(description="Expand the initial user question '[User's Question]' into a broader query that covers multiple aspects of the topic to ensure a comprehensive analysis.")
    step_back_question: str = Field(description="The modified query is:")

if __name__ == "__main__":
    question = "Hello How Are you?"
    # question = "What is the total sales amount for each product?"
    c = Text2SQLNode()
    print(c({"question": question}))
