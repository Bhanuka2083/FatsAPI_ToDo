import uuid
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import TaskCreate, UpdateTask
from app.models import Tasks


async def create_task(session: AsyncSession, data: TaskCreate) -> Tasks:
    task = Tasks(title = data.title, description=data.description)
    session.add(task)
    await session.flush()
    await session.refresh(task)
    return task


async def get_task(session: AsyncSession, task_id: uuid.UUID) -> Tasks | None:
    return await session.get(Tasks, task_id)

async def list_task(session: AsyncSession, *, only_pending: bool = False) -> Sequence[Tasks]:
    stmt = select(Tasks).order_by(Tasks.created_at.desc())
    if only_pending:
        stmt = stmt.where(Tasks.completed.is_(False))
    res = await session.execute(stmt)
    return res.scalars().all()


async def update_task(session: AsyncSession, task_id:uuid.UUID, data: UpdateTask) -> Tasks | None:
    task = await session.get(Tasks, task_id)
    if task is None:
        return None
    
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(task, field, value)

    await session.flush()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task_id:uuid.UUID) -> bool:
    task = await session.get(Tasks, task_id)
    if task is None:
        return False
    
    await session.delete(task)
    await session.flush()
    return True