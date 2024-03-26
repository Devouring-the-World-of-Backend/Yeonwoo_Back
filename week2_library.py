from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Dict, Optional
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient #테스트클라이언트 객체 사용해 테스트

app=FastAPI()

client=TestClient(app)

#특정 도메인 허용(문제 예)
origins=["https://example-fronted.com"]     

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


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

#사용자 정의 예외 클래스   
class UserdefinedERR(Exception):
    def __init__(self, book_id: int):
        self.book_id=book_id
        self.message=f"Book with ID {book_id} not found."
        super().__init__(self.message)

fake_db: Dict[int,Book]={}

#새로운 도서 추가
@app.post("/books/",response_model=Book,status_code=status.HTTP_201_CREATED)    
def create_book(book:Book):
    if book.id in fake_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Book ID already exists.")
    fake_db[book.id]=book
    return book

#모든 도서 목록
@app.get("/books/", response_model=List[Book])  
def all_books():
    return list(fake_db.values())

#도서 검색
@app.get("/books/{id}", response_model=Book)    
def read_book(id:int):
    if id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    return fake_db[id]

#도서 정보 업데이트
@app.put("/books/{id}", response_model=Book)     
def update_book(id:int, book_data:dict):
    if id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    updated_book=Book.from_user(book_data)
    fake_db[id]=updated_book
    return updated_book

#특정 도서 삭제
@app.delete("/books/{id}")      
def delete_book(id:int):
    if id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    del fake_db[id]
    return {"message": "Book deleted successfully."}

#도서 검색
@app.get("/books/search", response_model=List[Book])        
def search_book(title:str=None, author:str=None, published_year:int=None):
    result_books=[]
    for book in fake_db.values():
        if (title is None or book.title==title) and (author is None or book.author==author) and (published_year is None or book.published_year==published_year):
            result_books.append(book)
    return result_books

#도서 필터링 기능-년도별=>다중 필터링 기능
@app.get("/books/filter/",response_model=List[Book])
def filter_books(title: Optional[str] = None, author: Optional[str] = None, published_year: Optional[int] = None):
    filtered_books = []
    for book in fake_db.values():
        if (title is None or book.title==title) and (author is None or book.author==author) and (published_year is None or book.published_year==published_year):
            filtered_books.append(book)
    return filtered_books

#정렬 기능  **Query 매개변수 활용**
@app.get("/books/sort/",response_model=List[Book])
def sort_books(field: str = Query(..., description="정렬할 필드 (title, author, published_year)"), order: str = Query("asc", description="정렬 순서 (asc 또는 desc)")):
    if field not in {"title", "author", "published_year"}:
        raise HTTPException(status_code=400, detail="Invalid sorting field.")
    sorted_books = sorted(fake_db.values(), key=lambda x: getattr(x, field), reverse=(order == "desc"))
    return sorted_books

#예외 처리
@app.exception_handler(Exception)
async def validation_exception_handler(request,exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message":"Internal server error."}
    )

#전역 예외 핸들러
@app.exception_handler(UserdefinedERR)
async def exception_error(request,exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message":exc.message}
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