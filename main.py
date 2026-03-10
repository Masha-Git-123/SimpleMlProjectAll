from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Data model
class Task(BaseModel):
    id: int
    title: str
    description: str = None
    completed: bool = False

tasks = []

@app.get("/")
def home():
    return {"message": "Welcome to To-Do List API!"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.post("/tasks")
def add_task(task: Task):
    tasks.append(task.dict())
    return {"message": "Task added", "task": task}


# 🔽 Add this part at the very bottom 🔽
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
