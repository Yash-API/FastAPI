from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Todo

app = FastAPI()

# Create a new task
@app.post("/todos/")
async def create_todo(title: str, description: str = "", db: AsyncSession = Depends(get_db)):
    new_todo = Todo(title=title, description=description)
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    return new_todo

# Get all tasks with optional filtering by completed status
@app.get("/todos/")
async def get_todos(completed: bool = Query(None), db: AsyncSession = Depends(get_db)):
    query = select(Todo)
    if completed is not None:
        query = query.where(Todo.completed == completed)

    result = await db.execute(query)
    return result.scalars().all()

# Update a task (mark as completed)
@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, completed: bool, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        return {"error": "Task not found"}
    
    todo.completed = completed
    await db.commit()
    return {"message": "Task updated"}

# Delete a task
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        return {"error": "Task not found"}

    await db.delete(todo)
    await db.commit()
    return {"message": "Task deleted"}
