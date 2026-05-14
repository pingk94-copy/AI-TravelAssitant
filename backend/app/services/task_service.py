from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskResponse


def create_task(db: Session, user: User, task_type: str, input_json: dict[str, Any]) -> Task:
    task = Task(user_id=user.id, task_type=task_type, status="pending", input_json=input_json)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def complete_task(db: Session, task: Task, output_json: dict[str, Any]) -> Task:
    task.status = "success"
    task.output_json = output_json
    task.error_message = None
    db.commit()
    db.refresh(task)
    return task


def fail_task(db: Session, task: Task, error_message: str) -> Task:
    task.status = "failed"
    task.error_message = error_message
    db.commit()
    db.refresh(task)
    return task


def get_user_task(db: Session, user: User, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def to_task_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        task_type=task.task_type,
        status=task.status,
        input=task.input_json,
        output=task.output_json,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
