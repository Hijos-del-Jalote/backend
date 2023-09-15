from fastapi import FastAPI
from models import User,Ocupation
from uuid import UUID,uuid4
from typing import List
app = FastAPI()

db: List[User] = [
    User(
        id=uuid4(),
        first_name = "Pedro",
        ocupation = Ocupation.student),
    User(
        id=uuid4(),
        first_name = "Laura",
        ocupation = Ocupation.student),
]

@app.get("/")
async def root():
    return {"Hello": "World"}

@app.get("/api/v1/users")
async def fetch_users():
    return db

@app.post("/api/v1/users")
async def register_user(user: User):
    db.append(user)
    return {"id": user.id}

@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: UUID):
    for user in db:
        if user.id == user_id:
            db.remove(user)
    return {"id": user.id}