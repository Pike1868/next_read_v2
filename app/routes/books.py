from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Book, UserBooks, db
import requests
import os

books_bp = Blueprint('books_bp', __name__)

@books_bp.route('/search', methods=['GET'])
def search_google_books():
    startIndex = request.args.get('startIndex', 0, type=int)
    query = request.args.get('query', '')
    books = []

    if query:
        response = requests.get(
            f"https://www.googleapis.com/books/v1/volumes?q={query}&key={os.environ.get('API_KEY')}&startIndex={startIndex}&printType=books&maxResults=40"
        )
        
        data = response.json()

        if "items" in data:
            for item in data["items"]:
                book_info = item["volumeInfo"]
                sale_info = item.get("saleInfo", {})
                retail_price = sale_info.get("retailPrice", {})
                books.append({
                    "google_books_id": item["id"],
                    "title": book_info.get("title", "Unknown Title"),
                    "authors": book_info.get("authors", ["Unknown Author"]),
                    "thumbnail_url": book_info.get("imageLinks", {}).get("thumbnail", ""),
                    "published_date": book_info.get("publishedDate", "Date not available"),
                    "page_count": book_info.get("pageCount", "Page count not available"),
                    "categories": book_info.get("categories", ["No categories available"]),
                    "retail_price": retail_price.get("amount", "Price not available"),
                    "currency_code": retail_price.get("currencyCode", ""),
                })

    return jsonify(books=books, query=query, startIndex=startIndex)


@books_bp.route('/search_genre/<genre>', methods=["GET"])
def search_genre(genre):
    startIndex = request.args.get('startIndex', 0, type=int)
    genre_books = []
    response = requests.get(
        f"https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&startIndex={startIndex}&printType=books&maxResults=40"
    )
    data = response.json()

    if "items" in data:
        for item in data["items"]:
            book_info = item["volumeInfo"]
            genre_books.append({
                "google_books_id": item["id"],
                "title": book_info.get("title", "Unknown Title"),
                "authors": book_info.get("authors", ["Unknown Author"]),
                "thumbnail_url": book_info.get("imageLinks", {}).get("thumbnail", ""),
            })

    return jsonify(books=genre_books, query=genre, startIndex=startIndex)

@books_bp.route('/detail/<volume_id>', methods=['GET'])
def detail(volume_id):
    response = requests.get(
        f"https://www.googleapis.com/books/v1/volumes/{volume_id}?key={os.environ.get('API_KEY')}"
    )
    data = response.json()

    book_detail = data["volumeInfo"]

    return jsonify(book=book_detail, google_books_id=volume_id)

@books_bp.route('/save-book', methods=['POST'])
@jwt_required()
def save_book():
    user_id = get_jwt_identity()
    data = request.get_json()
    google_books_id = data.get('google_books_id')
    status = data.get('status')

    book = Book.query.filter_by(google_books_id=google_books_id).first()

    if not book:
        response = requests.get(
            f"https://www.googleapis.com/books/v1/volumes/{google_books_id}?key={os.environ.get('API_KEY')}"
        )
        data = response.json()["volumeInfo"]

        new_book = Book(
            google_books_id=google_books_id,
            title=data.get("title", "Unknown Title"),
            authors=", ".join(data.get("authors", ["Unknown Author"])),
            thumbnail_url=data.get("imageLinks", {}).get("thumbnail", ""),
            description=data.get("description", "No description available."),
            published_date=data.get("publishedDate", "Date not available"),
            average_rating=data.get("averageRating", None),
            ratings_count=data.get("ratingsCount", 0),
            page_count=data.get("pageCount")
        )

        db.session.add(new_book)
        db.session.flush()

        user_book_link = UserBooks(
            user_id=user_id, book_id=new_book.id, status=status)
        db.session.add(user_book_link)

    else:
        user_book_link = UserBooks.query.filter_by(
            user_id=user_id, book_id=book.id).first()

        if user_book_link:
            user_book_link.status = status
        else:
            user_book_link = UserBooks(
                user_id=user_id, book_id=book.id, status=status)
        db.session.add(user_book_link)

    db.session.commit()

    return jsonify({"msg": "Book saved successfully"}), 201

@books_bp.route('/<volume_id>/remove', methods=["POST"])
@jwt_required()
def remove_user_book(volume_id):
    user_id = get_jwt_identity()
    book_to_remove = Book.query.filter_by(google_books_id=volume_id).first()

    if not book_to_remove:
        return jsonify({"msg": "Book not found"}), 404

    user_book = UserBooks.query.filter_by(
        user_id=user_id, book_id=book_to_remove.id).first()

    if user_book:
        db.session.delete(user_book)
        db.session.commit()
        return jsonify({"msg": "Book removed successfully"}), 200
    else:
        return jsonify({"msg": "Book not found in your lists"}), 404
