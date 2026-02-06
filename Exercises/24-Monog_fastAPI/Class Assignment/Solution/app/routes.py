from typing import Optional
from fastapi import APIRouter, HTTPException, Path
from bson import ObjectId
from .models import TaskCreate, TaskUpdate, TaskResponse
from .crud import create_task, list_tasks, get_task, update_task, delete_task

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task_route(payload: TaskCreate):
    task = create_task(payload.dict())
    return task

@router.get("/", response_model=list[TaskResponse])
async def list_tasks_route(status: Optional[str] = None, priority: Optional[int] = None):
    tasks = list_tasks(status=status, priority=priority)
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_route(task_id: str = Path(..., regex=r'^[0-9a-fA-F]{24}$')):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task_route(task_id: str = Path(..., regex=r'^[0-9a-fA-F]{24}$'), payload: TaskUpdate = None):
    update_data = {k: v for k, v in payload.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    updated = update_task(task_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/{task_id}")
async def delete_task_route(task_id: str = Path(..., regex=r'^[0-9a-fA-F]{24}$')):
    ok = delete_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
