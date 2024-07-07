import chainlit as cl
from state_manager import ModelStateManager


@cl.on_chat_start
async def main():
    # logger.info("Starting chat...\n" + ("=" * 60))
    state_manager = ModelStateManager()
    cl.user_session.set('runnable', state_manager)


@cl.on_message
async def on_message(message: cl.Message):
    # logger.info('### Question:', message.content)
    state_manager = cl.user_session.get("runnable")
    answer_dict = state_manager.execute(question=message.content)
    # logger.info('### Answer:', answer_dict)
    content = None
    if not answer_dict.get("report_generation_results"):
        content = answer_dict['answer_generation']
    elements = None
    if not content:
        content = answer_dict["plot_generator_results"]["answer"]
        if answer_dict["report_generation_results"].get("plot_filename"):
            image_path = answer_dict["report_generation_results"]["plot_filename"]
            elements = [
                cl.Image(path=image_path, name="image1", display="inline"),
            ]

    msg = cl.Message(content=content, elements=elements)

    # async for chunk in runnable.astream(
    #     {"question": message.content},
    #     config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    # ):
    #     await msg.stream_token(chunk)

    await msg.send()