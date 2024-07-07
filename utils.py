from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from langchain_core.messages.base import BaseMessage
import json
from langchain_together import ChatTogether
from typing import Any

class AgentState(TypedDict):
    question: str
    db_data: dict
    text2sql_results: dict
    data_analytics_results: dict
    plot_generator_results: dict
    data_storytelling_results: dict
    report_generation_results: dict
    chat_history: list[BaseMessage]
    answer_generation: str


class ConfigManager(dict):
    def __init__(self) -> None:
        super().__init__()
        with open("configs.json") as f:
            self.update(json.loads(f.read()))


class LLM:
    def __init__(
        self, llm_source="togetherAI", additional_config: dict[str, Any] = {}
    ) -> None:
        self.llm_source = llm_source
        self.config = ConfigManager()
        self.additional_config = additional_config
        self.temperature = self.additional_config.get("temperature", 0.0)

        llm_init_map = {
            "togetherAI": self.init_togetherAI,
            "localMLX": self.init_localMLX,
            "openAI": self.init_openAI,
            "cluade": self.init_cluade,
        }
        self.llm_init = llm_init_map[llm_source]
        self.llm_init()
        # print(f"LLM initialized with source: {llm_source} and model: {self.model_name}")

    def init_togetherAI(self):
        self.model_name = self.additional_config.get(
            "model", "meta-llama/Llama-3-70b-chat-hf"
        )
        self.llm = ChatTogether(
            model=self.model_name,
            temperature=self.temperature,
            together_api_key=self.config["api"]["togetherAI"],
        )

    def init_cluade(self):
        self.model_name = self.additional_config.get("model", "claude-3-opus-20240229")
        # self.llm = ChatAnthropic(
        #     model=self.model_name,
        #     temperature=self.temperature,
        #     api_key=self.config["api"]["cluade"],
        # )

    def init_localMLX(self):
        from langchain_community.llms.mlx_pipeline import MLXPipeline
        from langchain_community.chat_models.mlx import ChatMLX

        # self.model_name = MLXPipeline.from_model_id("mlx-community/Meta-Llama-3-8B-Instruct-4bit")
        self.model_name = MLXPipeline.from_model_id(
            "mlx-community/Meta-Llama-3-8B-Instruct-8bit",
            pipeline_kwargs={"max_tokens": 256, "temp": 0.1},
        )
        self.llm = ChatMLX(llm=self.model_name)

    def init_openAI(self):
        self.model_name = "gpt-4o"

        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=300,
            timeout=None,
            max_retries=2,
            api_key=self.config["api"]["openAI"],
        )

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        print(f"LLM Input: args={args}, kwargs={kwds}")
        output = self.llm
        return output
