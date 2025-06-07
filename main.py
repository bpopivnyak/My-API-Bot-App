from unittest.mock import Base

import uvicorn

from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.future import engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from starlette import status
from pydantic import BaseModel

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BookCreate(BaseModel):
    name: str
    id: int

@app.get("/get_book/")
def read_users(db: Session = Depends(get_db)):
    return db.query(Book).all()

@app.post("/books/")
def create_user(book: BookCreate, db: Session = Depends(get_db)):
    db_user = Book(name=book.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user