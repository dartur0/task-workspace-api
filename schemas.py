from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "TODO"
    priority: Optional[str] = "MEDIUM"

class TaskCreate(TaskBase):
    board_id: int
    assignee_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    board_id: int
    assignee_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BoardBase(BaseModel):
    title: str

class BoardCreate(BoardBase):
    workspace_id: int

class BoardResponse(BoardBase):
    id: int
    workspace_id: int
    tasks: List[TaskResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

class WorkspaceBase(BaseModel):
    title: str
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceResponse(WorkspaceBase):
    id: int
    owner_id: int
    boards: List[BoardResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True