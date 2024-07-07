from typing import Any
from utils import AgentState, LLM
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import HumanMessage
from logging_config import LoggerManager, LogState
from langchain_openai import ChatOpenAI
import base64


class DataStorytellingNode:
    def __init__(self) -> None:
        self.llm = LLM("openAI")

    def forward(self, state: AgentState):
        LoggerManager.log_flow(f"Start with {self.llm.model_name}", node=self.__class__.__name__, state=LogState.START)

        image_path = state["plot_generator_results"]["plot_filename"]
        base64_image = self.encode_image(image_path)
        question = state['question']
        messages = [
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": (
                            "As an expert data analyst, using the initial question and the generated plot, provide a comprehensive and professional insight that answers the user's initial question."
                            "Ensure the narrative is suitable for a workplace environment, informative, correct, and complete."
                            "The insight should interpret the data shown in the plot, highlighting key trends, patterns, and anomalies. "
                            "Include relevant context, potential implications, and actionable recommendations based on the data. "
                            "The storytelling should be engaging and thorough, offering a clear explanation and meaningful conclusions that add value to the user's understanding of the data."
                            f"\n\ninitial question: {question}"
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                ]
            ),
        ]
        # prompt_template = ChatPromptTemplate.from_messages(messages)
        # chain = prompt_template | self.llm | StrOutputParser()
        # results = chain.invoke({"base64_image": base64_image})
        results = self.llm.llm.invoke(messages)
        state["data_storytelling_results"] = results.content
        LoggerManager.log_flow(
            f"Storytelling Results: {results}",
            node=self.__class__.__name__,
            state=LogState.RESPONSE,
        )
        return state

    def encode_image(self, image_path: str):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)


if __name__ == "__main__":
    c = DataStorytellingNode()
    print(c())
