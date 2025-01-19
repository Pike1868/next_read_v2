from datetime import datetime, timedelta
import time
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Book, UserBooks, BookRanking, FeaturedMeta, db
from .book_helpers import fetch_google_books_by_isbn, build_featured_lists_from_db  # Import helpers
from collections import defaultdict
import requests
import os

books_bp = Blueprint('books_bp', __name__)

CACHE = {}
CACHE_EXPIRY = 3600  # 1 hour cache expiry

@books_bp.route('/search', methods=['GET'])
def search_google_books():
    startIndex = request.args.get('startIndex', 0, type=int)
    query = request.args.get('query', '').lower()

    # Check cache
    cache_key = f"{query}_{startIndex}"
    if cache_key in CACHE:
        cached_result, timestamp = CACHE[cache_key]
        if time.time() - timestamp < CACHE_EXPIRY:
            print("Serving from cache.")
            return jsonify(cached_result)

    books = []

    if query:
        response = requests.get(
            f"https://www.googleapis.com/books/v1/volumes?q={query}&key={os.environ.get('API_KEY')}&startIndex={startIndex}&printType=books&maxResults=40"
        )
        data = response.json()

        if "items" in data:
            for item in data["items"]:
                book_info = item.get("volumeInfo", {})
                books.append({
                    "google_books_id": item.get("id"),
                    "title": book_info.get("title", "Unknown Title"),
                    "authors": book_info.get("authors", ["Unknown Author"]),
                    "thumbnail_url": book_info.get("imageLinks", {}).get("thumbnail", ""),
                    "published_date": book_info.get("publishedDate", "Date not available"),
                    "page_count": book_info.get("pageCount", "Page count not available"),
                    "categories": book_info.get("categories", ["No categories available"]),
                })

    # Cache the result
    CACHE[cache_key] = ({"books": books, "query": query, "startIndex": startIndex}, time.time())

    return jsonify(books=books, query=query, startIndex=startIndex)



@books_bp.route('/search-genre/<genre>', methods=["GET"])
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
            sale_info = item.get("saleInfo", {})
            retail_price = sale_info.get("retailPrice", {})
            genre_books.append({
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

    
    return jsonify(books=genre_books, query=genre, startIndex=startIndex)

@books_bp.route('/detail/<volume_id>', methods=['GET'])
def detail(volume_id):
    """Fetch detailed information about a book from Google Books API."""
    try:
        # If the volume_id starts with 'isbn_', treat it as an ISBN
        if volume_id.startswith("isbn_"):
            isbn = volume_id.replace("isbn_", "")
            # Search for the book by ISBN
            search_response = requests.get(
                f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={os.environ.get('API_KEY')}"
            )
            search_data = search_response.json()

            if "items" not in search_data:
                return jsonify({"error": "Book details not found"}), 404

            # Extract the correct volumeId
            volume_id = search_data["items"][0]["id"]

        # Now make a request to get detailed book information
        response = requests.get(
            f"https://www.googleapis.com/books/v1/volumes/{volume_id}?key={os.environ.get('API_KEY')}"
        )
        data = response.json()

        if "volumeInfo" not in data:
            return jsonify({"error": "Book details not found"}), 404

        book_detail = data.get("volumeInfo", {})
        sale_info = data.get("saleInfo", {})

        result = {
            "title": book_detail.get("title", "Unknown Title"),
            "authors": book_detail.get("authors", ["Unknown Author"]),
            "description": book_detail.get("description", "Description not available"),
            "publishedDate": book_detail.get("publishedDate", "Date not available"),
            "pageCount": book_detail.get("pageCount", 0),
            "categories": book_detail.get("categories", ["No categories available"]),
            "imageLinks": book_detail.get("imageLinks", {}),
            "publisher": book_detail.get("publisher", "Publisher not available"),
            "retailPrice": sale_info.get("retailPrice", {}).get("amount"),
            "currencyCode": sale_info.get("retailPrice", {}).get("currencyCode"),
        }

        return jsonify({"book": result}), 200

    except requests.exceptions.RequestException as e:
        # Capture the exception in Sentry
        sentry_sdk.capture_exception(e)
        return jsonify({"error": "Failed to fetch book details"}), 500



@books_bp.route('/save-book', methods=['POST'])
@jwt_required()
def save_book():
    user_id = get_jwt_identity()
    data = request.get_json()
    google_books_id = data.get('google_books_id')
    status = data.get('status')

    # Normalize status
    if status:
        status = status.lower().replace(" ", "_")

    # Validate status
    allowed_statuses = {'currently_reading', 'want_to_read', 'previously_read'}
    if status not in allowed_statuses:
        return jsonify({"msg": "Invalid status provided."}), 400

    # Check if the book already exists by title and author
    book = Book.query.filter_by(title=data.get('title'), authors=", ".join(data.get('authors', []))).first()

    if not book:
        # Fetch the book data from Google Books if it doesn't exist
        response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{google_books_id}?key={os.environ.get('API_KEY')}")
        book_data = response.json()["volumeInfo"]

        new_book = Book(
            google_books_id=google_books_id,
            title=book_data.get("title", "Unknown Title"),
            authors=", ".join(book_data.get("authors", ["Unknown Author"])),
            thumbnail_url=book_data.get("imageLinks", {}).get("thumbnail", ""),
            description=book_data.get("description", "No description available."),
            published_date=book_data.get("publishedDate", "Date not available"),
            average_rating=book_data.get("averageRating", None),
            ratings_count=book_data.get("ratingsCount", 0),
            page_count=book_data.get("pageCount"),
        )

        db.session.add(new_book)
        db.session.flush()

        user_book_link = UserBooks(user_id=user_id, book_id=new_book.id, status=status)
        db.session.add(user_book_link)

    else:
        # If the book already exists, just link it to the user
        user_book_link = UserBooks.query.filter_by(user_id=user_id, book_id=book.id).first()

        if user_book_link:
            user_book_link.status = status
        else:
            user_book_link = UserBooks(user_id=user_id, book_id=book.id, status=status)
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

@books_bp.route('/user-books', methods=['GET'])
@jwt_required()
def get_user_books():
    user_id = get_jwt_identity()

    # Fetch UserBooks based on their status
    user_books = UserBooks.query.filter_by(user_id=user_id).all()
    
    print("================+++++++>",user_books)

    # Organize the books by status
    currently_reading = [ub.book.to_dict() for ub in user_books if ub.status == 'currently_reading']
    previously_read = [ub.book.to_dict() for ub in user_books if ub.status == 'previously_read']
    want_to_read = [ub.book.to_dict() for ub in user_books if ub.status == 'want_to_read']

    # Debugging: Print serialized data
    print("Currently Reading:", currently_reading)
    print("Previously Read:", previously_read)
    print("Want to Read:", want_to_read)

    # Return the books as JSON
    return jsonify({
        'currently_reading': currently_reading,
        'previously_read': previously_read,
        'want_to_read': want_to_read,
    })
   
@books_bp.route('/featured', methods=['GET'])
def get_featured_books():
    """Return the NYTimes best-seller lists."""
    nyt_api_key = os.environ.get('NYT_API_KEY', '')
    if not nyt_api_key:
        return jsonify({"error": "NYT_API_KEY not configured."}), 500

    # Check if data is less than 24h old
    meta = FeaturedMeta.query.first()
    now = datetime.now()
    twenty_four_hours_ago = now - timedelta(hours=24)

    if meta and meta.last_updated and meta.last_updated > twenty_four_hours_ago:
        # Use cached data
        featured_lists = build_featured_lists_from_db()
        return jsonify({
            "bestsellers_date": None,
            "published_date": None,
            "featured_lists": featured_lists
        })

    # Fetch fresh data from NYTimes
    nytimes_url = f"https://api.nytimes.com/svc/books/v3/lists/full-overview.json?api-key={nyt_api_key}"
    try:
        response = requests.get(nytimes_url)
        data = response.json()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch NYTimes data: {str(e)}"}), 500

    results = data.get("results", {})
    all_lists = results.get("lists", [])
    featured_lists = []

    for list_obj in all_lists:
        list_name = list_obj.get("list_name")
        books = sorted(
            [
                {
                    "rank": book.get("rank"),
                    "title": book.get("title"),
                    "author": book.get("author"),
                    "book_image": book.get("book_image"),
                    "google_books_id": f'isbn_{book.get("primary_isbn13")}',
                }
                for book in list_obj.get("books", [])
            ],
            key=lambda x: x["rank"] or float("inf")  # Sort by rank, handle missing ranks gracefully
        )
        featured_lists.append({"list_name": list_name, "books": books})


    # Update FeaturedMeta
    if not meta:
        meta = FeaturedMeta(last_updated=now)
        db.session.add(meta)
    else:
        meta.last_updated = now

    db.session.commit()

    return jsonify({
        "bestsellers_date": results.get("bestsellers_date"),
        "published_date": results.get("published_date"),
        "featured_lists": featured_lists
    })