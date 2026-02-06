from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from .database import tasks_col
from .models import StatusEnum

def task_to_dict(task: Dict) -> Dict[str, Any]:
    """Convert Mongo doc to dict with _id as str."""
    if task and '_id' in task:
        task['id'] = str(task['_id'])
        del task['_id']
    return task

def create_task(payload: Dict) -> Dict[str, Any]:
    result = tasks_col.insert_one(payload)
    task = tasks_col.find_one({"_id": result.inserted_id})
    return task_to_dict(task)

def list_tasks(status: Optional[str] = None, priority: Optional[int] = None) -> List[Dict[str, Any]]:
    filter_query: Dict[str, Any] = {}
    if status:
        filter_query['status'] = status
    if priority:
        filter_query['priority'] = priority
    tasks = list(tasks_col.find(filter_query))
    return [task_to_dict(t) for t in tasks]

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    try:
        task = tasks_col.find_one({"_id": ObjectId(task_id)})
        return task_to_dict(task)
    except:
        return None

def update_task(task_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        # Use find_one_and_update for atomicity and return updated doc
        updated = tasks_col.find_one_and_update(
            {"_id": ObjectId(task_id)},
            {"$set": payload},
            return_document=True
        )
        return task_to_dict(updated)
    except:
        return None

def delete_task(task_id: str) -> bool:
    try:
        result = tasks_col.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0
    except:
        return False
