from fastapi import FastAPI
import models
from database import engine
from auth import router as auth_router
from workspaces import router as workspace_router
from tasks import router as tasks_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Workspace API",
    description="RESTful API for project management, workspaces, and team task tracking.",
    version="0.1.0"
)

app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(tasks_router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Task Workspace API is running successfully!"}