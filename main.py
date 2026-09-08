from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import models
from database import engine
from auth import router as auth_router
from workspaces import router as workspace_router
from tasks import router as tasks_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Workspace API")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(tasks_router)

@app.get("/app", response_class=HTMLResponse)
def serve_ui():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()