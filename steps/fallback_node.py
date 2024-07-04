from typing import Any
from utils import AgentState, LLM
from langchain_core.output_parsers import StrOutputParser
import logging
from logging_config import setup_logging
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, BaseMessage
from operator import itemgetter

setup_logging()
logger = logging.getLogger(__name__)


class Node:
    def __init__(self, llm=None) -> None:
        self.llm = (
            llm
            if llm is not None
            else LLM("togetherAI", additional_config={"temperature": 0.7})
        )

    def forward(self, state: AgentState):
        fallback_prompt = ChatPromptTemplate.from_template(
            (
                "You are a friendly assistant created by LLM Group in University of Tehran.\n"
                "Do not respond to queries that are not related to sales data or business.\n"
                "If a query is not related to sales data, acknowledge your limitations.\n"
                "Provide concise responses to only sales-related queries.\n\n"
                "Current conversation:\n\n{chat_history}\n\n"
                "human: {question}"
            )
        )

        fallback_chain = (
            {
                "question": itemgetter("question"),
                "chat_history": lambda x: "\n".join(
                    [
                        (
                            f"human: {msg.content}"
                            if isinstance(msg, HumanMessage)
                            else f"AI: {msg.content}"
                        )
                        for msg in x["chat_history"]
                    ]
                ),
            }
            | fallback_prompt
            | self.llm
            | StrOutputParser()
        )

        logger.info("### Forward method called with state: %s", state)
        question = state["question"]
        chat_history = (
            state["chat_history"] if state["chat_history"] is not None else []
        )
        generation = fallback_chain.invoke(
            {"question": question, "chat_history": chat_history}
        )
        logger.info("### Generation: %s", generation)

        # TODO: complete chat history
        return {"answer_generation": generation}

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.forward(*args, **kwds)


if __name__ == "__main__":
    c = Node()
    print(c())
