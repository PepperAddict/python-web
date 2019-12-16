import os
import requests
import json
from flask import Flask, jsonify, session, render_template, request, redirect
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
        books = db.execute('SELECT * FROM books LIMIT 100').fetchall()
    else: 
        books = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER('%{}%') OR LOWER(author) LIKE LOWER('%{}%') OR isbn LIKE '%{}%' LIMIT 100".format(result, result, result)).fetchall()
    return render_template('index.html', books=books, search=result, user=ruin)

@app.route("/api/<string:isbn>")
def api(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("KEY"), "isbns": isbn })
    if res.status_code == requests.codes["ok"]:
        review = res.json()
    else: 
        review = None

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    print(res)

    if review is not None and book is not None:
        bookJSON = {
            "isbn": isbn,
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "review_count": review["books"][0]["reviews_count"],
            "avg_rating": review["books"][0]["average_rating"],
        }
    else: 
        bookJSON = {"result": "Sorry, there was no information for this ISBN"}
        
    return jsonify(bookJSON)

@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def book(isbn):

    #get username
    ruin = session.get('user')
    commented = None

    # request api info
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("KEY"), "isbns": isbn })
    if res.status_code == requests.codes["ok"]:
        review = res.json()
    else: 
        review = None

    # rating
    rating = ['1', '2', '3', '4', '5']
    select = request.form.get('rating')

    # review
    reviewForm = request.form.get('review')

    # form submission
    if request.method == "POST":
        if select is not None and reviewForm is not None and ruin is not None:
            db.execute('INSERT INTO reviews (isbn, username, rating, review) VALUES (:isbn, :user, :rate, :rev)', 
                {"isbn": isbn, "user": ruin, "rate": select, "rev": reviewForm})
            db.commit()
            return redirect('/book/' + str(isbn))

    # book info from book db
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    # submitted review from review db
    userReview = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

    for x in userReview:
        if x.username == ruin:
            commented = True
    

    if book is None: 
        return render_template('error.html', message="No Book Found")

    return render_template('book.html', commented=commented, userReview=userReview, rating=rating, book=book, review=review, user=ruin)


@app.route("/register", methods=["GET", "POST"])
def regi():

        # let's check to see if user is already logged in
    ruin = session.get('user')
    if request.method == "GET":
        if ruin is not None: 
            return redirect('/')

    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    success = ''

    if name is not None and username is not None and password is not None:
        db.execute('INSERT INTO users (name, username, password) VALUES (:name, :username, :password)',
            {"name": name, "username": username, "password": password})
        success = "Successfully Registered"
        session['user'] = username
        db.commit()
        return redirect('/')

    return render_template('register.html', success=success, name=name, username=username, password=password)

@app.route("/login", methods=["GET", "POST"])
def login():

    # let's check to see if user is already logged in
    ruin = session.get('user')
    if request.method == "GET":
        if ruin is not None: 
            return redirect('/')

    username = request.form.get('username')
    password = request.form.get('password')

    if request.method == "POST":
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
