import os
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, selectinload, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from typing import List

#async engine
DATABASE_URL="sqlite:///library.db"
async_engine=create_async_engine(DATABASE_URL, echo=True)
async_session=sessionmaker(async_engine,expire_on_commit=False, class_=AsyncSession)

app=FastAPI()


#create session
Session=sessionmaker(bind=async_engine)
session=Session()

Base=declarative_base()

#define book
class Book(Base):
    __tablename__='books'

    id=Column(Integer, primary_key=True)
    title=Column(String)
    author=Column(String)
    description=Column(String)
    published_year=Column(Integer)
    category=relationship("Category",secondary="book_category")

#define user
class User(Base):
    __tablename__='users'

    id=Column(Integer, primary_key=True)
    name=Column(String)
    phonenum=Column(String)

#category as different class
class Cateogory(Base):
    __tablename__='categories'

    id=Column(Integer, primary_key=True)
    name=Column(String)

#define rent
class Rent(Base):
    __tablename__='rent'
    #user and book id as foreign key
    id=Column(Integer, primary_key=True)
    user_id=Column(Integer,ForeignKey('users.id'))
    book_id=Column(Integer, ForeignKey('books.id'))
    returned=Column(Boolean, default=False)

    #create relationship between user, book and rental
    user=relationship("User",back_populates="rent")
    book=relationship("Book", back_populates="rent")

User.rent=relationship("Rent",back_populates="user")
Book.rent=relationship("Rent", back_populates="book")

#@app.get("/books/",response_model=List[Book])
#async def get_books():

#CREATE
#add new book
new_book=Book(title='BOOOK', author='Author', description='description', published_year='2024')
session.add(new_book)

#add new user
new_user=User(name='NAmE', phonenum='01011111111')
session.add(new_user)

#renting book
def rent_book(user,book):
    rental=Rent(user=user,book=book)
    session.add(rental)

#READ
#print booklist
booklist=session.query(Book).all()
for book in booklist:
    print("Title: %s, author: %s, description: %s, published_year: %d",book.title, book.author, book.description, book.published_year)

#UPDATE
#update book info
alterbook=session.query(Book).filter_by(title='BOOOK').first()
if alterbook:
    alterbook.author='New author' 
    session.commit()

#DELETE
#delete book from db
deletebook=session.query(Book).filter_by(title='New Book').first()
if deletebook:
    session.delete(deletebook)
    session.commit()   

book_category=Table('book_category',Base.metadata,Column('book_id',Integer,ForeignKey('books.id'),Column('category_id',Integer,ForeignKey('categories.id'))))

Base.metadata.create_all(async_engine)

