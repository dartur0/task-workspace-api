from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas, security

router = APIRouter(tags=["Boards & Tasks"])

@router.post("/boards/", response_model=schemas.BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(
    board_data: schemas.BoardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == board_data.workspace_id).first()
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found or access denied")
        
    new_board = models.Board(title=board_data.title, workspace_id=board_data.workspace_id)
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return new_board

@router.post("/tasks/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    board = db.query(models.Board).filter(models.Board.id == task_data.board_id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
        
    new_task = models.Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        board_id=task_data.board_id,
        assignee_id=task_data.assignee_id or current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.patch("/tasks/{task_id}/status", response_model=schemas.TaskResponse)
def update_task_status(
    task_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    task.status = new_status
    db.commit()
    db.refresh(task)
    return task