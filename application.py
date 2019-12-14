import os
import requests
import json
from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():
    ruin = session.get('user')
    result = request.form.get('search')
    if result is None:
        books = db.execute('SELECT * FROM books LIMIT 30').fetchall()
    else: 
        books = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER('%{}%') OR LOWER(author) LIKE LOWER('%{}%') OR isbn LIKE '%{}%' LIMIT 30".format(result, result, result)).fetchall()
    return render_template('index.html', books=books, search=result, user=ruin)

@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def book(isbn):
    ruin = session.get('user')
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("KEY"), "isbns": isbn })
    review = res.json()

    rating = ['1', '2', '3', '4', '5']
    select = request.form.get('rating')
    session['rating'] = select
    rate = session.get('rating')

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None: 
        return render_template('error.html', rating=rating, message="No Book Found")

    return render_template('book.html', rate=rate, rating=rating, book=book, review=review, user=ruin)


@app.route("/register", methods=["GET", "POST"])
def regi():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    success = ''

    if name is not None and username is not None and password is not None:
        db.execute('INSERT INTO users (name, username, password) VALUES (:name, :username, :password)',
            {"name": name, "username": username, "password": password})
        success = "Successfully Registered"
        db.commit()

    return render_template('register.html', success=success, name=name, username=username, password=password)

@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
    if user is not None:
        session['user'] = username
        return redirect('/')
    else:
        session['user'] = None
    
    return render_template('login.html')

@app.route("/logout", methods=["POST"])
def logout():
    session['user'] = None
    return redirect('/')

@app.route("/review", methods=["POST"])
def review():
    select = request.form.get('rating')
    session['rating'] = select