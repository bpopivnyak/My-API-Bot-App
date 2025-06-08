import secrets
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette import status
from starlette.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel


DATABASE_URL = "sqlite:///./store.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
templates = Jinja2Templates(directory="templates")

class Book(Base):
    __tablename__ = "Books"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

security = HTTPBasic()
class UserLogin(BaseModel):
    username: str
    password: str

def check_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
@app.delete("/secure-endpoint/")
def secure_endpoint(username=Depends(check_credentials)):
    return {"message": f"Hello, {username}! You are authorized."}

book: List[dict] = [
    {"id": 1, "name": "Олена Іваненко", "email": "olena@example.com", "city": "Київ"},
    {"id": 2, "name": "Андрій Петренко", "email": "andriy@example.com", "city": "Львів"},
    {"id": 3, "name": "Марія Коваленко", "email": "maria@example.com", "city": "Одеса"},
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    name: str

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db), username: str = Depends(check_credentials)):
    db_user = Book(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/")
def read_users(
    db: Session = Depends(get_db),
    username: str = Depends(check_credentials)
):
    return db.query(Book).all()


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    username: str = Depends(check_credentials)
):
    for u in book:
        if u["id"] == user_id:
            book.remove(u)
            return {"message": f"Користувача видалено користувачем: {username}"}
    raise HTTPException(status_code=404, detail="Користувача не знайдено")

uvicorn.run(app)