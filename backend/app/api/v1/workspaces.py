import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, AuthenticatedUser
from app.db.session import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from app.services import workspace as workspace_service

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    data: WorkspaceCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """Create a new workspace for the authenticated user."""
    return workspace_service.create_workspace(db=db, owner_id=current_user.id, data=data)


@router.get("", response_model=List[WorkspaceResponse])
def list_workspaces(
    limit: int = 50,
    offset: int = 0,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WorkspaceResponse]:
    """List workspaces belonging to the authenticated user."""
    return workspace_service.list_workspaces(
        db=db,
        owner_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """Retrieve workspace details. Returns 404 if not found or unauthorized."""
    workspace = workspace_service.get_workspace(db=db, owner_id=current_user.id, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: uuid.UUID,
    data: WorkspaceUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """Update workspace details if owned by current user."""
    workspace = workspace_service.update_workspace(
        db=db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
        data=data,
    )
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a workspace and cascade delete its contents."""
    deleted = workspace_service.delete_workspace(
        db=db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
