import uuid
from collections.abc import Sequence
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import your modules (adjust paths based on your structure)
from app.database import get_session, init_db, kill_engine
from app.schemas import TaskCreate, UpdateTask, TaskRead
from app.crud import create_task, get_task, list_task, update_task, delete_task


app = FastAPI(
    title="Todo API",
    description="An asynchronous CRUD API for managing tasks",
    version="1.0.0"
)

# --- Lifecycle Events ---

@app.on_event("startup")
async def on_startup() -> None:
    """Runs when the API starts; initializes tables."""
    await init_db()

@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Runs when the API stops; cleans up connection pool."""
    await kill_engine()


# --- API Routes ---

@app.post(
    "/tasks", 
    response_model=TaskRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
async def api_create_task(
    data: TaskCreate, 
    session: AsyncSession = Depends(get_session)
):
    """Creates a new task in the database using validation rules."""
    return await create_task(session=session, data=data)


@app.get(
    "/tasks", 
    response_model=Sequence[TaskRead],
    summary="List all tasks"
)
async def api_list_tasks(
    only_pending: bool = False, 
    session: AsyncSession = Depends(get_session)
):
    """Retrieves tasks sorted newest first. Can filter by pending status."""
    return await list_task(session=session, only_pending=only_pending)


@app.get(
    "/tasks/{task_id}", 
    response_model=TaskRead,
    summary="Get a single task by ID"
)
async def api_get_task(
    task_id: uuid.UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Fetches a specific task using its UUID7 string."""
    task = await get_task(session=session, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Task with ID {task_id} not found"
        )
    return task


@app.patch(
    "/tasks/{task_id}", 
    response_model=TaskRead,
    summary="Partially update a task"
)
async def api_update_task(
    task_id: uuid.UUID, 
    data: UpdateTask, 
    session: AsyncSession = Depends(get_session)
):
    """Updates only the fields provided in the request payload."""
    task = await update_task(session=session, task_id=task_id, data=data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Task with ID {task_id} not found"
        )
    return task


@app.delete(
    "/tasks/{task_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
async def api_delete_task(
    task_id: uuid.UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Permanently deletes a task from the database."""
    success = await delete_task(session=session, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Task with ID {task_id} not found"
        )
    # 204 No Content responses return nothing
    return None


@app.get("/", summary="Root Welcome Endpoint")
async def root():
    return {"message": "Welcome to the Todo API! Head over to /docs to view endpoints."}


