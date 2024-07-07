from typing import Any
from utils import AgentState
from typing import Any
from utils import AgentState, LLM
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from logging_config import LoggerManager, LogState


class DataAnalyticsNode:
    def __init__(self) -> None:
        self.llm = LLM("togetherAI")
        # self.llm = LLM("openAI")
        # self.llm = LLM("cluade")

    def forward(self, state: AgentState):
        LoggerManager.log_flow(f"Start with {self.llm.model_name}", node=self.__class__.__name__, state=LogState.START)

        # Load the CSV file
        csv_path = state["text2sql_results"]["csv_path"]
        df = pd.read_csv(csv_path)

        # Generate summary of the CSV file
        summary_text = self.generate_summary_text(df)

        # Formulate hypothesis based on the summary and user question
        user_question = state["question"]
        hypothesis = self.formulate_hypothesis(summary_text, user_question)

        # Update state with summary and hypothesis
        state["data_analytics_results"] = {"summary_text": summary_text, "hypothesis": hypothesis}

        LoggerManager.log_flow(f"State updated with data analytics results:\n{state['data_analytics_results']}", node=self.__class__.__name__, state=LogState.RESPONSE)
        return state

    def generate_summary_text(self, df: pd.DataFrame) -> str:
        summary_lines = []

        summary_lines.append(f"Shape of the data: {df.shape}")

        summary_lines.append("Columns with sample data and their data types:")
        for col in df.columns:
            dtype = df[col].dtype
            sample = df[col].iloc[0]
            summary_lines.append(f"  - {col}: {sample} ({dtype})")

        return "\n".join(summary_lines)

    def formulate_hypothesis(self, summary_text: str, user_question: str) -> str:
        prompt_template = PromptTemplate(
            template="Given the user question and the CSV summary, generate a hypothesis about what data analytics insight and chart the user wants.\n\nUser question: {user_question}\n\nCSV summary:\n{summary_text}\n\nHypothesis:",
            input_variables=["user_question", "summary_text"]
        )

        chain = prompt_template | self.llm | StrOutputParser()

        result = chain.invoke({"user_question": user_question, "summary_text": summary_text})
        return result

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)


if __name__ == "__main__":
    c = DataAnalyticsNode()
    print(c())
