import os
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, selectinload, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from typing import List

#async engine
DATABASE_URL="sqlite:///mydatabase.db"
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
    __tablename__='rentals'
    #user and book id as foreign key
    id=Column(Integer, primary_key=True)
    user_id=Column(Integer,ForeignKey('users.id'))
    book_id=Column(Integer, ForeignKey('books.id'))
    returned=Column(Boolean, default=False)

    #create relationship between user, book and rental
    user=relationship("User",back_populates="rentals")
    book=relationship("Book", back_populates="rentals")

User.rentals=relationship("Rental",back_populates="user")
Book.rentals=relationship("Rental", back_populates="book")

#@app.get("/books/",response_model=List[Book])
#async def get_books():



    

book_category=Table('book_category',Base.metadata,Column('book_id',Integer,ForeignKey('books.id'),Column('category_id',Integer,ForeignKey('categories.id'))))

Base.metadata.create_all(async_engine)

