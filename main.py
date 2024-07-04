import logging
from logging_config import setup_logging
from pydantic import BaseModel
from state_manager import ModelStateManager
import chainlit as cl

setup_logging()
logger = logging.getLogger(__name__)

state_manager = ModelStateManager()


class QuestionForm(BaseModel):
    question: str


@cl.on_chat_start
async def on_chat_start():
    logger.info("Starting chat...\n" + ("=" * 60))
    await cl.Message(
        content="Hello I am AI assistant. Ask a question from your database."
    ).send()
    state_manager = ModelStateManager()
    cl.user_session.set("runnable", state_manager)


@cl.on_message
async def on_message(message: cl.Message):
    logger.info("### Question:", message.content)
    state_manager = cl.user_session.get("runnable")
    answer_dict = state_manager.execute(question=message.content)
    logger.info("### Answer:", answer_dict)
    content = answer_dict["answer_generation"]
    elements = None
    if content == None:
        content = answer_dict["plot_generator_results"]["answer"]
        code = answer_dict["plot_generator_results"]["plot_code"]
        image_path = answer_dict["report_generation_results"]["plot_filename"]
        elements = [
            cl.Image(path=image_path, name="image1", display="inline"),
            cl.Text(code, language="python"),
        ]

    msg = cl.Message(content=content, elements=elements)

    # TODO: stream the output
    # async for chunk in runnable.astream(
    #     {"question": message.content},
    #     config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    # ):
    #     await msg.stream_token(chunk)

    await msg.send()
