from utils import AgentState, LLM
from langchain.schema.messages import HumanMessage
from logging_config import LoggerManager, LogState
import base64
import os
import json

class LlmJugment:
    def __init__(self, final_report_directory:str) -> None:
        self.llm = LLM("cluade")
        self.report = self.read_final_io(final_report_directory)

    def read_final_io(self, final_report_directory:str):
        report_file = os.path.join(final_report_directory, "final_output.json")

        if not os.path.exists(report_file):
            raise FileNotFoundError(f"No report found with the number {final_report_directory.split('/')[-1]}.")

        with open(report_file, "r") as f:
            log_message = json.load(f)
        
        return log_message

    def encode_image(self, image_path: str):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def eval_relevancy(self):
        image_path = self.report["image_path"]
        base64_image = self.encode_image(image_path)
        initial_question = self.report["initial_input"]
        generated_insight = self.report["final_output"]

        messages = [
            HumanMessage(
                content=f"""Analyze the relevancy of the generated report based on the initial question, the generated chart, and the generated insight. Assess how accurately and comprehensively it addresses the user's initial question. After your analysis, provide a relevancy score out of 100.

Initial Question: {initial_question}
Generated Chart: (See attached image)
Generated Insight: {generated_insight}

Analysis and score (0-100) Relevancy:"""
            ),
            HumanMessage(
                content={"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ),
        ]

        results = self.llm.llm.invoke(messages)
        print('### Relevancy:', results)
        return results.content

    def eval_insightfulness(self):
        image_path = self.report["image_path"]
        base64_image = self.encode_image(image_path)
        initial_question = self.report["initial_input"]
        generated_insight = self.report["final_output"]

        messages = [
            HumanMessage(
                content=f"""Analyze the insightfulness of the generated report, considering the initial question, the generated chart, and the generated insight. Evaluate the depth, usefulness, and actionability of the insights provided. After your analysis, provide an insightfulness score out of 100.

Initial Question: {initial_question}
Generated Chart: (See attached image)
Generated Insight: {generated_insight}

Analysis and score (0-100) of the Insightfulness:"""
            ),
            HumanMessage(
                content={"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ),
        ]

        results = self.llm.llm.invoke(messages)
        print('### Insightfulness:', results)
        return results.content

    def eval_quality(self):
        LoggerManager.log_flow(f"Start with {self.llm.model_name}", node=self.__class__.__name__, state=LogState.START)

        image_path = self.report["image_path"]
        base64_image = self.encode_image(image_path)
        initial_question = self.report["initial_input"]
        generated_insight = self.report["final_output"]

        messages = [
            HumanMessage(
                content=f"""Analyze the data storytelling quality of the generated report, considering the initial question, the generated chart, and the generated insight. Evaluate how effectively it combines data and narrative to convey a coherent and engaging story. After your analysis, provide a data storytelling quality score out of 100.

Initial Question: {initial_question}
Generated Chart: (See attached image)
Generated Insight: {generated_insight}

Analysis and score (0-100) of the
Data Storytelling Quality:"""
            ),
            HumanMessage(
                content={"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ),
        ]

        results = self.llm.llm.invoke(messages)
        print('### Quality:', results)
        return results.content
