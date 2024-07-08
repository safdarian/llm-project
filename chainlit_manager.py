import chainlit as cl
from state_manager import ModelStateManager
from logging_config import LoggerManager, LogState
from utils import AgentState

# Initialize the state manager
state_manager = ModelStateManager()

@cl.on_chat_start
async def on_chat_start():
    fallback_state = {
                "last_executed_state": "node0",
                "num_fallbacks": 0,
                "fallback": False,
                "fallback_type": None,
                "fallback_desc": None,
                "fallback_confirm_response": None,
                "fallback_error_response": None,
                "current_state": 0,
                "fallbacks": [0, 2, 2, 2, 2],
                "outputs": [0, 1, 1, 1, 1]
            }
    cl.user_session.set("fallback_state", fallback_state)
    await cl.Message(
        content="Hello, I am your AI assistant. Ask a question from your database."
    ).send()
    LoggerManager.log_flow("Chatbot started...\n" + ("=" * 40))

@cl.on_message
async def on_message(message: cl.Message):
    LoggerManager.log_flow_metric(node='Question', content=f'"{message.content}"', state=LogState.RESULT)
    LoggerManager.log_flow(f"### Prompt: \"{message.content}\"")
    fallback_state = cl.user_session.get("fallback_state")


    # Text to SQL
    answer_dict: AgentState = state_manager.execute({"question":message.content}, fallback_info=fallback_state)
    LoggerManager.log_flow_metric(node='Answer', content=answer_dict, state=LogState.RESULT)
    fallback_state = answer_dict["fallback_info"]

    if not answer_dict.get("answer_generation"):


        special_message = fallback_state["confirm_premessage"]
        res_continue = await cl.AskActionMessage(
            content="{}\n{}\nContinue?".format(special_message, fallback_state["fallback_desc"]),
            actions=[
                cl.Action(name="continue", value="continue", label="✅ Yes"),
                cl.Action(name="cancel", value="cancel", label="❌ No"),
                ],
                ).send()
        await cl.Message(content= special_message + "\n" + fallback_state["fallback_desc"]).send()
        if res_continue and res_continue.get("value") == "continue":

            fallback_state["fallbacks"][fallback_state["current_state"]] = 0
            # fallback_state["outputs"][fallback_state["current_state"]] = 0
            fallback_state["current_state"] += 1
            
        else:
            fallback_state["fallbacks"][fallback_state["current_state"]] = 1
            # fallback_state["outputs"][fallback_state["current_state"]] = 0
            
            res_hint = await cl.AskUserMessage(content="Give me a hint", timeout=50).send()
            if res_hint:
                fallback_state["fallback_confirm_response"] = res_hint["output"]
                
            answer_dict: AgentState = state_manager.execute(answer_dict, fallback_info=fallback_state)
            fallback_state = answer_dict["fallback_info"]
            special_message = fallback_state["confirm_premessage"]
            res_continue = await cl.AskActionMessage(
                content="{}\n{}\nContinue?".format(special_message, fallback_state["fallback_desc"]),
                actions=[
                    cl.Action(name="continue", value="continue", label="✅ Continue"),
                    ],
                    ).send()
            await cl.Message(content= special_message + "\n" + fallback_state["fallback_desc"]).send()
            fallback_state["fallbacks"][fallback_state["current_state"]] = 0
            fallback_state["current_state"] += 1

        # Analytics
        answer_dict = state_manager.execute(answer_dict, fallback_info=fallback_state)
        fallback_state = answer_dict["fallback_info"]
        

        special_message = fallback_state["confirm_premessage"]
        res_continue = await cl.AskActionMessage(
            content="{}\n{}\nContinue?".format(special_message, fallback_state["fallback_desc"]),
            actions=[
                cl.Action(name="continue", value="continue", label="✅ Yes"),
                cl.Action(name="cancel", value="cancel", label="❌ No"),
                ],
                ).send()
        await cl.Message(content= special_message + "\n" + fallback_state["fallback_desc"]).send()
        if res_continue and res_continue.get("value") == "continue":

            fallback_state["fallbacks"][fallback_state["current_state"]] = 0
            # fallback_state["outputs"][fallback_state["current_state"]] = 0
            fallback_state["current_state"] += 1
            
        else:
            fallback_state["fallbacks"][fallback_state["current_state"]] = 1
            # fallback_state["outputs"][fallback_state["current_state"]] = 0
            
            res_hint = await cl.AskUserMessage(content="Give me a hint", timeout=50).send()
            if res_hint:
                fallback_state["fallback_confirm_response"] = res_hint["output"]
                
            answer_dict: AgentState = state_manager.execute(answer_dict, fallback_info=fallback_state)
            fallback_state = answer_dict["fallback_info"]
            special_message = fallback_state["confirm_premessage"]
            res_continue = await cl.AskActionMessage(
                content="{}\n{}\nContinue?".format(special_message, fallback_state["fallback_desc"]),
                actions=[
                    cl.Action(name="continue", value="continue", label="✅ Continue"),
                    ],
                    ).send()
            await cl.Message(content= special_message + "\n" + fallback_state["fallback_desc"]).send()
            fallback_state["fallbacks"][fallback_state["current_state"]] = 0
            fallback_state["current_state"] += 1

        # Plot Generator
        answer_dict = state_manager.execute(answer_dict, fallback_info=fallback_state)
        fallback_state = answer_dict["fallback_info"]
        

        special_message = fallback_state["confirm_premessage"]
        res_continue = await cl.AskActionMessage(
            content="{}\n{}\nContinue?".format(special_message, fallback_state["fallback_desc"]),
            actions=[
                cl.Action(name="continue", value="continue", label="✅ Yes"),
                cl.Action(name="cancel", value="cancel", label="❌ No"),
                ],
                ).send()
        await cl.Message(content= special_message + "\n" + fallback_state["fallback_desc"]).send()
        if res_continue and res_continue.get("value") == "continue":

            fallback_state["fallbacks"][fallback_state["current_state"]] = 0
            # fallback_state["outputs"][fallback_state["current_state"]] = 0
            fallback_state["current_state"] += 1
            
        else:
            fallback_state["fallbacks"][fallback_state["current_state"]] = 1
            # fallback_state["outputs"][fallback_state["current_state"]] = 0
            
            res_hint = await cl.AskUserMessage(content="Give me a hint", timeout=50).send()
            if res_hint:
                fallback_state["fallback_confirm_response"] = res_hint["output"]
                
            answer_dict: AgentState = state_manager.execute(answer_dict, fallback_info=fallback_state)
            fallback_state = answer_dict["fallback_info"]
            special_message = fallback_state["confirm_premessage"]
            res_continue = await cl.AskActionMessage(
                content="{}\n{}\nContinue?".format(special_message, fallback_state["fallback_desc"]),
                actions=[
                    cl.Action(name="continue", value="continue", label="✅ Continue"),
                    ],
                    ).send()
            await cl.Message(content= special_message + "\n" + fallback_state["fallback_desc"]).send()
            fallback_state["fallbacks"][fallback_state["current_state"]] = 0
            fallback_state["current_state"] += 1
        

        # Data StoryTelling
        answer_dict = state_manager.execute(answer_dict, fallback_info=fallback_state)
        fallback_state = answer_dict["fallback_info"]
        
        
        special_message = fallback_state["confirm_premessage"]
        res_continue = await cl.AskActionMessage(
            content="{}\n{}\nContinue?".format(special_message, fallback_state["fallback_desc"]),
            actions=[
                cl.Action(name="continue", value="continue", label="✅ Yes"),
                cl.Action(name="cancel", value="cancel", label="❌ No"),
                ],
                ).send()
        await cl.Message(content= special_message + "\n" + fallback_state["fallback_desc"]).send()
        if res_continue and res_continue.get("value") == "continue":
        
            fallback_state["fallbacks"][fallback_state["current_state"]] = 0
            # fallback_state["outputs"][fallback_state["current_state"]] = 0
            fallback_state["current_state"] += 1
            
        else:
            fallback_state["fallbacks"][fallback_state["current_state"]] = 1
            # fallback_state["outputs"][fallback_state["current_state"]] = 0
            
            res_hint = await cl.AskUserMessage(content="Give me a hint", timeout=50).send()
            if res_hint:
                fallback_state["fallback_confirm_response"] = res_hint["output"]
                
            answer_dict: AgentState = state_manager.execute(answer_dict, fallback_info=fallback_state)
            fallback_state = answer_dict["fallback_info"]
            special_message = fallback_state["confirm_premessage"]
            res_continue = await cl.AskActionMessage(
                content="{}\n{}\nContinue?".format(special_message, fallback_state["fallback_desc"]),
                actions=[
                    cl.Action(name="continue", value="continue", label="✅ Continue"),
                    ],
                    ).send()
            await cl.Message(content= special_message + "\n" + fallback_state["fallback_desc"]).send()
            fallback_state["fallbacks"][fallback_state["current_state"]] = 0
            fallback_state["current_state"] += 1


    content = answer_dict.get("answer_generation")
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
    fallback_state = {
                "last_executed_state": "node0",
                "num_fallbacks": 0,
                "fallback": False,
                "fallback_type": None,
                "fallback_desc": None,
                "fallback_confirm_response": None,
                "fallback_error_response": None,
                "current_state": 0,
                "fallbacks": [0, 2, 2, 2, 2],
                "outputs": [0, 1, 1, 1, 1]
            }
    cl.user_session.set("fallback_state", fallback_state)
    LoggerManager.save_final_io(answer_dict)