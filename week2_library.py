from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List, Dict
from datetime import datetime

app=FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str
    description: str
    published_year: int

    @validator("published_year")
    def check_year(cls,v):
        if v>datetime.now().year:
            raise ValueError("Published year can't be in the future.")
        return v


fake_db: Dict[int,Book]={}

@app.post("/books/")    #새로운 도서 추가
def create_book(book:Book):
    fake_db[book.id]=book
    return {"message":"Book created successfully."}

@app.get("/books/", response_model=List[Book])  #모든 도서 목록
def all_books():
    return list(fake_db.values())

@app.get("/books/{id}", response_model=Book)    #도서 검색
def read_book(id:int):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Book not found.")
    return fake_db[id]

@app.put("/books/{id}")     #도서 정보 업데이트
def update_book(id:int, book:Book):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Book not found.")
    fake_db[id]=book
    return {"message":"Book updated successfully."}

@app.delete("/books/{id}")      #특정 도서 삭제
def delete_book(id:int):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Book not found.")
    del fake_db[id]
    return {"message": "Book deleted successfully."}

@app.get("/books/search", response_model=List[Book])        #도서 검색
def search_book(title:str=None, author:str=None, published_year:int=None):
    result_books=[]
    for book in fake_db.values():
        if (title is None or book.title==title) and (author is None or book.author==author) and (published_year is None or book.published_year==published_year):
            result_books.append(book)
    return result_books