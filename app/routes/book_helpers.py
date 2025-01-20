import requests
import os
import time
from collections import defaultdict
from ..models import Book, BookRanking, db
from functools import wraps

# Caching API Responses
CACHE = {}
CACHE_EXPIRY = 60 * 60 * 24  # 24 hours

# Throttling for API Requests
REQUEST_INTERVAL = 0.1  # 100ms between requests

def cache_results(expiry=None):
    """
    Decorator to cache function results for a specified duration.
    """
    if expiry is None:
        expiry = 3600  # Default expiry if not provided

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            if cache_key in CACHE:
                cached_result, timestamp = CACHE[cache_key]
                if time.time() - timestamp < expiry:
                    print("Serving from cache:", func.__name__)
                    return cached_result
            result = func(*args, **kwargs)
            CACHE[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator


def fetch_google_books_by_isbn(isbn13):
    """
    Fetch a single book's data from Google Books using the ISBN13 number.
    Returns a dictionary with relevant Google Books fields or None if not found.
    """
    google_books_api_key = os.environ.get('API_KEY', '')
    if not google_books_api_key:
        print("Warning: No Google Books API key found (API_KEY).")
        return None

    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn13}&key={google_books_api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching Google Books data:", e)
        return None

    items = data.get("items", [])
    if not items:
        return None

    volume_info = items[0].get("volumeInfo", {})
    google_book_id = items[0].get("id")

    return {
        "google_books_id": google_book_id,
        "title": volume_info.get("title"),
        "authors": ", ".join(volume_info.get("authors", [])),
        "published_date": volume_info.get("publishedDate", "Unknown"),
        "description": volume_info.get("description", "No description available."),
        "thumbnail_url": volume_info.get("imageLinks", {}).get("thumbnail", ""),
        "page_count": volume_info.get("pageCount"),
    }

def build_featured_lists_from_db():
    """
    Read from BookRanking (and its related Book) to reconstruct a `featured_lists` structure.
    """
    all_rankings = (
        db.session.query(BookRanking)
        .join(Book, BookRanking.book_id == Book.id)
        .order_by(BookRanking.list_name, BookRanking.rank)  # Order by list name and rank
        .all()
    )

    lists_dict = defaultdict(list)

    for rank_entry in all_rankings:
        lists_dict[rank_entry.list_name].append({
            "rank": rank_entry.rank,
            "google_books_id": rank_entry.book.google_books_id,
            "title": rank_entry.book.title,
            "author": rank_entry.book.authors,
            "thumbnail_url": rank_entry.book.thumbnail_url,
            "description": rank_entry.book.description,
        })

    # Convert the dictionary to a list of lists
    return [
        {"list_name": list_name, "display_name": list_name, "books": books}
        for list_name, books in lists_dict.items()
    ]



def throttle_api_request(api_call, *args, **kwargs):
    """Throttle API requests by introducing a delay."""
    time.sleep(REQUEST_INTERVAL)  # Pause before making the request
    return api_call(*args, **kwargs)


def get_cached_book_data(google_books_id):
    """Retrieve cached book data if it exists and is not expired."""
    cached_book = CACHE.get(google_books_id)
    if cached_book and time.time() - cached_book["timestamp"] < CACHE_EXPIRY:
        return cached_book["data"]
    return None

def cache_book_data(google_books_id, data):
    """Cache book data for a given Google Books ID."""
    CACHE[google_books_id] = {"data": data, "timestamp": time.time()}


def hydrate_nyt_books(book_data_list):
    """
    Hydrate NYT books with data from the database or Google Books API.
    """
    hydrated_books = []
    for book in book_data_list:
        # Check if the book is already in the database
        existing_book = Book.query.filter_by(google_books_id=book["google_books_id"]).first()
        if existing_book:
            book.update({
                "title": existing_book.title,
                "authors": existing_book.authors.split(", "),
                "thumbnail_url": existing_book.thumbnail_url,
                "description": existing_book.description,
            })
            
            
        else:
            # Fetch data from the API
            isbn = book["google_books_id"].replace("isbn_", "")
            response = requests.get(
                f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={os.environ.get('API_KEY')}"
            )
            if response.status_code == 200:
                data = response.json()
                book_info = data.get("items", [{}])[0].get("volumeInfo", {})
                book.update({
                    "title": book_info.get("title", "Unknown Title"),
                    "authors": book_info.get("authors", ["Unknown Author"]),
                    "thumbnail_url": book_info.get("imageLinks", {}).get("thumbnail", ""),
                    "description": book_info.get("description", "No description available."),
                })
                # Save the book to the database
                new_book = Book(
                    google_books_id=book["google_books_id"],
                    title=book["title"],
                    authors=", ".join(book["authors"]),
                    thumbnail_url=book["thumbnail_url"],
                    description=book["description"],
                )
                db.session.add(new_book)
                db.session.commit()
        hydrated_books.append(book)
    return hydrated_books


