from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from functools import wraps
import sqlite3



app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.secret_key = 'secret_key'
#db = SQLAlchemy(app)


app.config["SESSION_PERMENANT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
"""

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/home')
@login_required
def home():
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    #print("users:",users)
    
    return render_template('home.html',username=session["username"] , users=users)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",(username, password))
        conn.commit()

        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = ?",(username, ))
        user = cursor.fetchall()
        if len(user) > 0:
            if user[0][2] == password:
                session["username"] = request.form["username"]
                return redirect(url_for('home'))

        flash('Incorrect username or password!')
    return render_template('login.html')

"""
@app.before_first_request
def create_tables():
    db.create_all()
"""




if __name__ == '__main__':
    app.run(debug=True)