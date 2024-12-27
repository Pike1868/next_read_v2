# README: Next Read Version 2

## Project Overview

**Next Read Version 2** is the backend API for the Next Read application, which helps people who want to read more. This version is focused on providing a robust and scalable API using Python and Flask. The API handles user authentication, book management, and interaction with external services like the Google Books API.


## Getting Started

### Prerequisites

-   Python 3.x
-   pip

# Installation Instructions

#### 1. Clone the repository:

```bash
git clone https://github.com/pike1868/next_read_v2.git
cd next_read_v2
```

#### 2. Install PostgreSQL:
Ensure that **PostgreSQL** is installed on your system. You can follow the installation instructions for **PostgreSQL** based on your operating system.

- **Linux (Ubuntu)**: Install **PostgreSQL** using:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

- **Windows**: Download and install **PostgreSQL** from [the official website](https://www.postgresql.org/download/windows/).

After installation, verify **psql** is accessible by running:

```bash
psql --version
```

#### 3. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 4. Install dependencies:

```bash
pip install -r requirements.txt
```

#### 5. Set up the `.env` file:

In the root directory of your project, create a `.env` file and populate it with the following keys (replace the placeholder values with your actual configuration):

```env
SECRET_KEY="your_secret_key_here"
DEBUG=True
APP_SETTINGS=config.Config
DATABASE_URI="postgresql://your_username:your_password@localhost:5432/your_database_name"
FLASK_APP=app.__init__:create_app
FLASK_DEBUG=1
TEST_DATABASE_URI="postgresql://your_username:your_password@localhost:5432/your_test_database"
API_KEY="your_api_key_here"
```

- **`DATABASE_URI`**: This should be the **PostgreSQL connection string**. Replace `your_username`, `your_password`, and `your_database_name` with your actual database details.
- **`API_KEY`**: If your app interacts with an external API, make sure to provide your actual API key here.

#### 6. Run the application:

```bash
python run.py
```

This will start your **Flask** application. You should now be able to access it at `http://127.0.0.1:5000/` in your browser.

---

#### Additional Notes:
- Make sure **PostgreSQL** is running and accepting connections on `localhost:5432`. If you’re using a **custom port** or **remote PostgreSQL server**, adjust the `DATABASE_URI` accordingly.

- If you're using **Windows** and **WSL** for the development environment, ensure that your PostgreSQL is set up to accept connections from WSL, and use the correct IP/hostname.

- You can create the PostgreSQL database with the following SQL commands:

```sql
CREATE DATABASE your_database_name;
CREATE DATABASE your_test_database;
```

### Endpoints

#### User Authentication

-   **Sign Up:** `@users_bp.route('/sign-up', methods=["GET", "POST"])`
-   **Sign In:** `@users_bp.route('/sign-in', methods=["GET", "POST"])`
-   **Edit Profile:** `@users_bp.route("/profile/edit", methods=["GET", "POST"])`
-   **Sign Out:** `@users_bp.route("/sign-out", methods=["POST"])`
-   **Delete User:** `@users_bp.route("/delete", methods=["POST"])`

#### Book Management

-   **Search Books (Google API):** `@books_bp.route('/search', methods=['POST'])`
-   **Genre-based Search:** `@books_bp.route('/search-genre/<genre>', methods=["GET", "POST"])`
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
