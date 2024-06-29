import uvicorn
from uvicorn.config import LOGGING_CONFIG
import logging
from logging_config import setup_logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from state_manager import ModelStateManager
import chainlit as cl

setup_logging()
logger = logging.getLogger(__name__)

state_manager = ModelStateManager()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class QuestionForm(BaseModel):
    question: str

# @app.get("/", response_class=HTMLResponse)
# def get_form(request: Request):
#     logger.info("GET request received at root endpoint")
#     return templates.TemplateResponse("index.html", {"request": request, "answer": None, "image": None})

# @app.post("/", response_class=HTMLResponse)
# def post_form(request: Request, question: str = Form(...)):
#     logger.info(f"POST request received with question: {question}")
#     answer_dict = state_manager.execute(question=question)
#     logger.info(f"Answer dictionary: {answer_dict}")
#     answer = answer_dict["plot_generator_results"]["answer"]
#     image_url = answer_dict["report_generation_results"]["plot_filename"]
#     return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "question": question, "image": image_url})

# if __name__ == "__main__":
#     logger.info("Starting server...\n" + ("=" * 60))
#     uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)

@cl.on_chat_start
async def on_chat_start():
    logger.info("Starting chat...\n" + ("=" * 60))
    await cl.Message(content="Hello I am AI assistant. Ask a question from your database.").send()
    state_manager = ModelStateManager()
    cl.user_session.set('runnable', state_manager)

@cl.on_message
async def on_message(message: cl.Message):
    logger.info('### Question:', message.content)
    state_manager = cl.user_session.get("runnable")
    answer_dict = state_manager.execute(question=message.content)
    logger.info('### Answer:', answer_dict)
    content = answer_dict['answer_generation']
    elements = None
    if content==None:
        content = answer_dict["plot_generator_results"]["answer"]
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