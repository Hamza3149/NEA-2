from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from functools import wraps
import sqlite3


app = Flask(__name__)

app.config["SESSION_PERMENANT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.after_request
def after_request(response):
    """Ensure responses aren"t cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/home")
@login_required
def home():
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    print("users:",users)
    
    return render_template("home.html",username=session["username"] , users=users)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE username = ?",(username, ))
        existing_users = cursor.fetchall()

        if len(existing_users) > 0:
            flash("That username already exists")
        
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",(username, password))
        conn.commit()

        session["username"] = username

        return redirect("/home")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM users WHERE username = ?",(username, ))
        user = cursor.fetchall()
        if len(user) > 0 and user[0][2] == password:
            session["username"] = request.form["username"]
            return redirect("/home")

        flash("Incorrect username or password!")
    return render_template("login.html")

