from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)

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
    cc="SELECT * FROM character;"
    cc=query_db(cc)
    return render_template("home.html", cc=cc)


if __name__ == "__main__":
    app.run(debug=True)