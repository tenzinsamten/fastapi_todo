from fastapi import FastAPI, Body, HTTPException

from model.book import Book
from model.book_request import BookRequest
from starlette import status

app = FastAPI()

BOOKS = [
    Book(1, 'title', 'samten', 'description', 5)
]


@app.get("/books",status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.post("/books",status_code=status.HTTP_201_CREATED)
async def create_new_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    return BOOKS.append(new_book)


@app.get("/books/{title}")
async def get_book_by_title(title: str):
    for book in BOOKS:
        if book.get('title').casefold() == title.casefold():
            return book
    raise HTTPException(status_code=404, detail='Not found')
