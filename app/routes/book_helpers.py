import requests
import os
from collections import defaultdict
from ..models import Book, BookRanking, db
from functools import wraps

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

def hydrate_nyt_books(books):
    """
    Enrich NYT books with additional data from Google Books using their google_books_id.
    """
    hydrated_books = []
    for book in books:
        google_books_id = book.get("google_books_id")
        if google_books_id and google_books_id.startswith("isbn_"):
            isbn = google_books_id.replace("isbn_", "")
            book_data = fetch_google_books_by_isbn(isbn)
            if book_data:
                book.update(book_data)  # Enrich with Google Books data
        hydrated_books.append(book)
    return hydrated_books
