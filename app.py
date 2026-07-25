from flask import Flask, render_template, g, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "p943j8ow7kw9p05e7qkw0"

DATABASE = "database.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    db = get_db()
    cursor = db.execute(query, args)
    results = cursor.fetchall()
    cursor.close()

    if one:
        return results[0] if results else None

    return results

def execute_db(query, args=()):
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()

    return cursor.lastrowid


@app.route("/")
def home():
    session.clear()
    cc="SELECT * FROM character;"
    posts="SELECT * FROM posts ORDER BY time ASC;"
    cc=query_db(cc)
    posts=query_db(posts)
    return render_template("home.html", cc=cc, posts=posts)

@app.route("/contact")
def contact():
    session.clear()
    return render_template("contact.html")

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    return render_template("admin.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = query_db(
            "SELECT * FROM admin WHERE username = ?",
            (username,),
            one=True
        )

        if user and check_password_hash(user["password"], password):
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("admin"))
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)