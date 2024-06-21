from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from state_manager import ModelStateManager

state_manager = ModelStateManager()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class QuestionForm(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": None, "image": None})

@app.post("/", response_class=HTMLResponse)
def post_form(request: Request, question: str = Form(...)):
    answer_dict = state_manager.execute(question=question)
    print(answer_dict)
    answer = answer_dict["plot_generator_results"]["answer"]
    image_url = answer_dict["report_generation_results"]["plot_filename"]
    return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "question": question, "image": image_url})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
