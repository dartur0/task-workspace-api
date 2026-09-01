from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas, security

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.post("/", response_model=schemas.WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace_data: schemas.WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    new_workspace = models.Workspace(
        title=workspace_data.title,
        description=workspace_data.description,
        owner_id=current_user.id
    )
    db.add(new_workspace)
    db.commit()
    db.refresh(new_workspace)
    return new_workspace

@router.get("/", response_model=List[schemas.WorkspaceResponse])
def get_my_workspaces(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    workspaces = db.query(models.Workspace).filter(models.Workspace.owner_id == current_user.id).all()
    return workspaces

@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to delete this workspace"
        )
        
    db.delete(workspace)
    db.commit()
    return None