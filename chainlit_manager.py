import chainlit as cl
from state_manager import ModelStateManager
from logging_config import LoggerManager, LogState
from utils import AgentState

# Initialize the state manager
state_manager = ModelStateManager()

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content="Hello, I am your AI assistant. Ask a question from your database."
    ).send()
    LoggerManager.log_flow("Chatbot started...\n" + ("=" * 40))

@cl.on_message
async def on_message(message: cl.Message):
    LoggerManager.log_flow_metric(node='Question', content=f'"{message.content}"', state=LogState.RESULT)
    LoggerManager.log_flow(f"### Prompt: \"{message.content}\"")

    answer_dict: AgentState = state_manager.execute(question=message.content)

    LoggerManager.log_flow_metric(node='Answer', content=answer_dict, state=LogState.RESULT)
    content = answer_dict["answer_generation"]
    elements = None
    
    # Check if there are storytelling results and a plot image
    if answer_dict.get("data_storytelling_results"):
        content = answer_dict["data_storytelling_results"]
        if answer_dict["plot_generator_results"].get("plot_filename"):
            image_path = answer_dict["plot_generator_results"]["plot_filename"]
            elements = [
                cl.Image(path=image_path, name="image1", display="inline"),
            ]
    
    msg = cl.Message(content=content, elements=elements)

    await msg.send()
    LoggerManager.save_final_io(answer_dict)