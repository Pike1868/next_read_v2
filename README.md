# README: Next Read Version 2

## Project Overview

**Next Read Version 2** is the backend API for the Next Read application, which helps people who want to read more. This version is focused on providing a robust and scalable API using Python and Flask. The API handles user authentication, book management, and interaction with external services like the Google Books API.


## Getting Started

### Prerequisites

-   Python 3.x
-   pip

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/pike1868/next_read_v2.git
    cd next_read_v2
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:

    ```bash
    python run.py
    ```
### Endpoints

#### User Authentication

-   **Sign Up:** `@users_bp.route('/sign_up', methods=["GET", "POST"])`
-   **Sign In:** `@users_bp.route('/sign_in', methods=["GET", "POST"])`
-   **Edit Profile:** `@users_bp.route("/profile/edit", methods=["GET", "POST"])`
-   **Sign Out:** `@users_bp.route("/sign_out", methods=["POST"])`
-   **Delete User:** `@users_bp.route("/delete", methods=["POST"])`

#### Book Management

-   **Search Books (Google API):** `@books_bp.route('/search', methods=['POST'])`
-   **Genre-based Search:** `@books_bp.route('/search_genre/<genre>', methods=["GET", "POST"])`
-   **Book Details:** `@books_bp.route('/detail/<volume_id>')`
-   **Save Book:** `@books_bp.route('/save-book', methods=['POST'])`
-   **Remove Book:** `@books_bp.route('/<volume_id>/remove', methods=["POST"])`

### Project Directory Structure

```
next_read_book_tracker_v2/
│
├── app/
│ ├── init.py
│ ├── config.py
│ ├── models.py
│ ├── routes/
│ │ ├── users.py
│ │ └── books.py
│ ├── tests/
│ │ ├── test_books.py
│ │ └── test_users.py
├── venv/
├── .env
├── run.py
├── requirements.txt
└── README.md
```


## Why I Chose This Project

### Problem Statement and Goal

The main objective is to create a platform for both avid readers and beginners who aspire to read more. I wanted to build an app that allowed users to track their books and see the progress on their reading habits, and eventually allow users to create and track their reading goals. This app aims to make book discovery both easy and personalized by offering book recommendations based on a user's favorite genres, authors, and previously read books.

### Target Demographics

The primary users of this platform are:

-   Individuals passionate about reading and on the lookout for their next book to read.
-   People who want to keep tabs on their reading habits.
-   Anyone aspiring to cultivate a reading habit to enjoy the many benefits that reading provides, as highlighted [here](https://www.healthline.com/health/benefits-of-reading-books).

### Demographics by Stats

-   **Reading Patterns:** 19% of US adults are responsible for 79% of books read annually, as indicated in this article [research](https://journals.sagepub.com/doi/full/10.1177/1367549419886026).
-   **Gender Distribution:** Another interesting bit of information I found: According to data gathered by Zippia, 64.3% of readers are women, while 35.7% are men. More details can be found [here](https://myclasstracks.com/us-book-reading-statistics/).

### Additional Resources

-   Initial Project Proposal: <https://docs.google.com/document/d/1HtxSaqOavbiUVMYkoIC5m8_OQVsrk3ADwcKqpKc-AJg/edit>

-   Database Schema: <https://docs.google.com/document/d/1QJm9H24GYfQvAfwihd47M6fNrUKKpRvfEfBLsxm5TrQ/edit?usp=sharing>
