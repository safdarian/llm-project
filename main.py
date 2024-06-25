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

setup_logging()
logger = logging.getLogger(__name__)

state_manager = ModelStateManager()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class QuestionForm(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    logger.info("GET request received at root endpoint")
    return templates.TemplateResponse("index.html", {"request": request, "answer": None, "image": None})

@app.post("/", response_class=HTMLResponse)
def post_form(request: Request, question: str = Form(...)):
    logger.info(f"POST request received with question: {question}")
    answer_dict = state_manager.execute(question=question)
    logger.info(f"Answer dictionary: {answer_dict}")
    answer = answer_dict["plot_generator_results"]["answer"]
    image_url = answer_dict["report_generation_results"]["plot_filename"]
    return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "question": question, "image": image_url})

if __name__ == "__main__":
    logger.info("Starting server...\n" + ("=" * 60))
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)