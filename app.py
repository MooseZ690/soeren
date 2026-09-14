from flask import Flask, render_template, g, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, json

def load_content():
    with open("data/content.json", "r") as f:
        return json.load(f)

app = Flask(__name__)
app.secret_key = "p943j8ow7kw9p05e7qkw0"

DATABASE = "data/database.db"

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
    message = request.args.get("message")

    posts = query_db(
        "SELECT * FROM posts ORDER BY time DESC;"
    )

    history = query_db(
        """
        SELECT year, title, description, medals, position
        FROM history
        ORDER BY year DESC;
        """
    )

    content = load_content()

    return render_template(
        "home.html",
        content=content,
        posts=posts,
        history=history,
        message=message
    )

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    content = load_content()
    users = query_db("SELECT * FROM users ORDER BY time DESC;")

    if request.method == "POST":
        print(request.form)

        action = request.form.get("action")

        if action == "newpost":
            title = request.form["title"]
            post_content = request.form["content"]

            execute_db(
                "INSERT INTO posts (title, content) VALUES (?, ?)",
                (title, post_content)
            )

        elif action == "update_character":
            print("UPDATING JSON - CC")

            content["name"] = request.form["name"]
            content["subheading"] = request.form["subheading"]
            content["description"] = request.form["description"]

            print(content)

            with open("data/content.json", "w") as f:
                json.dump(content, f, indent=2)

        elif action == "update_email":
            print("UPDATING JSON - EMAIL CONTENT")

            content["mail_subject"] = request.form["subject"]
            content["mail_body"] = request.form["body"]

            print(content)

            with open("data/content.json", "w") as f:
                json.dump(content, f, indent=2)


        return redirect(url_for("admin"))

    return render_template("admin.html", content=content, users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
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

@app.route("/toggle_sent/<int:id>")
def toggle_sent(id):
    execute_db("""
        UPDATE users
        SET sent = CASE WHEN sent = 1 THEN 0 ELSE 1 END
        WHERE id = ?
    """, (id,))

    return redirect(request.referrer or "/")

@app.route("/sendemail", methods=["GET", "POST"])
def sendemail():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']

        existing_user = query_db(
            "SELECT * FROM users WHERE email = ?",
            (email,),
            one=True
        )

        if existing_user:
            return redirect(url_for("contact"))

        execute_db(
            "INSERT INTO users (name, email, sent) VALUES (?, ?, 0)",
            (name, email)
        )
    return redirect(url_for("home", message=True))

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        desc = request.form["description"]

        existing_user = query_db(
            "SELECT * FROM booking WHERE email = ?",
            (email,),
            one=True
        )

        if existing_user:
            return redirect(url_for("contact"))

        execute_db(
            "INSERT INTO users (name, email, sent) VALUES (?, ?, 0)",
            (name, email)
        ) #registering as a user too

        execute_db(
            """
            INSERT INTO booking (name, email, desc, sent)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, desc, 0)
        )

    return redirect(url_for("home", message=True))

@app.route("/admin/email", methods=["GET", "POST"])
def admin_email():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    content = load_content()

    if request.method == "POST":
        content["mail_subject"] = request.form["mail_subject"]
        content["mail_body"] = request.form["mail_body"]

        with open("data/content.json", "w") as f:
            json.dump(content, f, indent=4)

        return redirect(url_for("admin_email"))

    return render_template(
        "admin_email.html",
        content=content
    )

@app.route("/logout", methods=["POST"])
def logout():
        session.clear()
        print("session cleared")
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
