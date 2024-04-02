from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app=FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str
    description: str
    published_year: int

fake_db: Dict[int,Book]={}

@app.post("/books/")
def create_book(book:Book):
    fake_db[book.id]=book
    return {"message":"Book created successfully."}

@app.get("/books/", response_model=List[Book])
def all_books():
    return list(fake_db.values())

@app.get("/books/{id}", response_model=Book)
def read_book(id:int):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Book not found.")
    return fake_db[id]

@app.put("/books/{id}")
def update_book(id:int, book:Book):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Book not found.")
    fake_db[id]=book
    return {"message":"Book updated successfully."}

@app.delete("/books/{id}")
def delete_book(id:int):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Book not found.")
    del fake_db[id]
    return {"message": "Book deleted successfully."}