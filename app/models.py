from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""
    db.app = app


class User(db.Model):
    """User table..."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    bio = db.Column(db.Text)
    location = db.Column(db.Text)
    image_url = db.Column(db.Text, default="/static/images/default-pic.png")
    creation_date = db.Column(
        db.DateTime, nullable=False, default=datetime.now)
    hashed_password = db.Column(db.Text, nullable=False)

    books = db.relationship('UserBooks', backref='user', cascade='all, delete')

    @property
    def formatted_date(self):
        """Return nicely-formatted date."""
        return self.creation_date.strftime("%a %b %-d  %Y, %-I:%M %p")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @staticmethod
    def hash_password(password):
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.hashed_password, password)

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.hashed_password = User.hash_password(password)


class Book(db.Model):
    """Books table..."""

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    google_books_id = db.Column(db.Text, nullable=False, unique=True)
    title = db.Column(db.Text, nullable=False)
    authors = db.Column(db.Text, nullable=False)
    thumbnail_url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    published_date = db.Column(db.Text)
    average_rating = db.Column(db.Float)
    ratings_count = db.Column(db.Integer)
    page_count = db.Column(db.Integer)

    users = db.relationship('UserBooks', backref='book', cascade='all, delete')

    def to_dict(self):
        """Serialize book instance to dictionary."""
        return {
            'google_books_id': self.google_books_id,
            'title': self.title,
            'authors': self.authors.split(', ') if self.authors else [],
            'thumbnail_url': self.thumbnail_url,
            'description': self.description,
            'published_date': self.published_date,
            'average_rating': self.average_rating,
            'ratings_count': self.ratings_count,
            'page_count': self.page_count,
        }


class UserBooks(db.Model):
    """Link table for Users <-> Books with status and reading progress."""
    
    __tablename__ = 'user_books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='cascade'))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id", ondelete='cascade'))
    status = db.Column(db.String(50), nullable=False)

    # new columns for reading progress
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    current_page = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return (f"<UserBooks id={self.id} user_id={self.user_id} "
                f"book_id={self.book_id} status={self.status} "
                f"start_date={self.start_date} end_date={self.end_date} "
                f"current_page={self.current_page}>")


class BookRanking(db.Model):
    """
    A table to store ranks from various lists/services.

    example:
      - list_name = 'NYT'   with rank=1
      - list_name = 'GOOGLE'  with rank=3
    """
    __tablename__ = "book_rankings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'))

    # e.g. 'nyt', 'google', 'usa_today', 'bookbub', etc.
    list_name = db.Column(db.String(100), nullable=False)

    # The numeric position in that list
    rank = db.Column(db.Integer)

    # Date or version when this rank was valid
    bestsellers_date = db.Column(db.Date, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # relationship back to Book
    book = db.relationship("Book", backref="book_rankings")

    def __repr__(self):
        return f"<BookRanking book_id={self.book_id} list_name={self.list_name} rank={self.rank}>"

class FeaturedMeta(db.Model):
    """
    Tracks the last time we fetched bestsellers data from NYT
    (so we can skip refetching if it’s less than 24h old, for instance).
    """
    __tablename__ = 'featured_meta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    last_updated = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<FeaturedMeta id={self.id} last_updated={self.last_updated}>"
