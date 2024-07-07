from logging_config import LoggerManager, LogState
from pydantic import BaseModel
from state_manager import ModelStateManager

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from chainlit.utils import mount_chainlit




app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


if __name__ == "__main__":
    mount_chainlit(app=app, target="chainlit_manager.py", path="")
    # logger.info("Starting server...\n" + ("=" * 60))
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
