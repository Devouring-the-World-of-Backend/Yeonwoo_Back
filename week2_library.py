from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, validator
from typing import List, Dict
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient #테스트클라이언트 객체 사용해 테스트
#from src.api.main import app  #httpx import

#client=TestClient(app)
client=TestClient()

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
    
    @classmethod
    def from_user(cls,book_data):
        return cls(**book_data)


fake_db: Dict[int,Book]={}

@app.post("/books/",response_model=Book,status_code=status.HTTP_201_CREATED)    #새로운 도서 추가
def create_book(book:Book):
    if book.id in fake_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Book ID already exists.")
    fake_db[book.id]=book
    return book

@app.get("/books/", response_model=List[Book])  #모든 도서 목록
def all_books():
    return list(fake_db.values())

@app.get("/books/{id}", response_model=Book)    #도서 검색
def read_book(id:int):
    if id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    return fake_db[id]

@app.put("/books/{id}", response_model=Book)     #도서 정보 업데이트
def update_book(id:int, book_data:dict):
    if id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    updated_book=Book.from_user(book_data)
    fake_db[id]=updated_book
    return updated_book

@app.delete("/books/{id}")      #특정 도서 삭제
def delete_book(id:int):
    if id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    del fake_db[id]
    return {"message": "Book deleted successfully."}

@app.get("/books/search", response_model=List[Book])        #도서 검색
def search_book(title:str=None, author:str=None, published_year:int=None):
    result_books=[]
    for book in fake_db.values():
        if (title is None or book.title==title) and (author is None or book.author==author) and (published_year is None or book.published_year==published_year):
            result_books.append(book)
    return result_books

#예외 처리
@app.exception_handler(Exception)
async def validation_exception_handler(request,exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message":"Internal server error."}
    )

#test create book
def test_create_book():
    response=client.post("/books/", json={"id":1, "title": "testbook", "author": "testauthor", "description": "testdescription", "published_year": 2022})
    assert response.status_code == 201
    response = client.post("/books/", json={"id": 1, "title": "testbook", "author": "testauthor", "description": "testdescription", "published_year": 2022})
    assert response.status_code == 409

#test update book
def test_update_book():
    response = client.put("/books/100", json={"title": "newtitle"})
    assert response.status_code == 404

#test delete book
def test_delete_book():
    response = client.delete("/books/100")
    assert response.status_code == 404