import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


def create_workspace(db: Session, owner_id: uuid.UUID, data: WorkspaceCreate) -> Workspace:
    """Create a new workspace owned by the authenticated user."""
    workspace = Workspace(
        name=data.name.strip(),
        owner_id=owner_id,
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


def list_workspaces(db: Session, owner_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[Workspace]:
    """List all workspaces owned by the user."""
    stmt = (
        select(Workspace)
        .where(Workspace.owner_id == owner_id)
        .order_by(Workspace.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_workspace(db: Session, owner_id: uuid.UUID, workspace_id: uuid.UUID) -> Optional[Workspace]:
    """Retrieve an owned workspace by ID. Returns None if not found or unauthorized."""
    stmt = select(Workspace).where(
        Workspace.id == workspace_id,
        Workspace.owner_id == owner_id,
    )
    return db.scalars(stmt).first()


def update_workspace(
    db: Session,
    owner_id: uuid.UUID,
    workspace_id: uuid.UUID,
    data: WorkspaceUpdate,
) -> Optional[Workspace]:
    """Update workspace name if owned by the user."""
    workspace = get_workspace(db, owner_id, workspace_id)
    if not workspace:
        return None

    if data.name is not None:
        workspace.name = data.name.strip()
        db.commit()
        db.refresh(workspace)

    return workspace


def delete_workspace(db: Session, owner_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
    """Delete an owned workspace and its cascaded resources."""
    workspace = get_workspace(db, owner_id, workspace_id)
    if not workspace:
        return False

    db.delete(workspace)
    db.commit()
    return True
