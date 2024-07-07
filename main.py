from logging_config import LoggerManager, LogState
from pydantic import BaseModel
from state_manager import ModelStateManager
import chainlit as cl

state_manager = ModelStateManager()


class QuestionForm(BaseModel):
    question: str


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content="Hello I am AI assistant. Ask a question from your database."
    ).send()
    LoggerManager.log_flow("Chatbot started...\n" + ("=" * 40))


@cl.on_message
async def on_message(message: cl.Message):
    LoggerManager.log_flow_metric(node='Question', content=f'"{message.content}"', state=LogState.RESULT)
    LoggerManager.log_flow(f"### Prompt: \"{message.content}\"")
    answer_dict = state_manager.execute(question=message.content)
    print("### Answer:", answer_dict)
    LoggerManager.log_flow_metric(node='Answer', content=answer_dict, state=LogState.RESULT)
    content = answer_dict["answer_generation"]
    elements = None
    if content == None:
        content = answer_dict["plot_generator_results"]["answer"]
        code = answer_dict["plot_generator_results"]["plot_code"]
        image_path = answer_dict["report_generation_results"]["plot_filename"]
        elements = [
            cl.Image(path=image_path, name="image1", display="inline"),
            # cl.Text(code),
        ]

    msg = cl.Message(content=content, elements=elements)

    # TODO: stream the output
    # async for chunk in runnable.astream(
    #     {"question": message.content},
    #     config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    # ):
    #     await msg.stream_token(chunk)

    await msg.send()
