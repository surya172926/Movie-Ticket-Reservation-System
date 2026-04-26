from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- MOVIE IMAGES ----------------
movie_images = {
    "RRR": "rrr.jpg",
    "Pushpa": "pushpa.jpg",
    "KGF": "kgf.png",
    "Salaar": "salaar.jpg"
}

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            username TEXT,
            movie TEXT,
            seats TEXT
        )
    """)
    conn.commit()
    conn.close()

create_tables()

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    if "user" not in session:
        return redirect("/login")

    movies = ["RRR", "Pushpa", "KGF", "Salaar"]

    return render_template(
        "home.html",
        movies=movies,
        movie_images=movie_images
    )

# -------- LOGIN --------
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get('username')
        pwd = request.form.get('password')

        conn = get_db()
        data = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user, pwd)
        ).fetchone()
        conn.close()

        if data:
            session["user"] = user
            return redirect("/")
        else:
            return "Invalid Credentials ❌"

    return render_template("login.html")

# -------- REGISTER --------
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form.get('username')
        pwd = request.form.get('password')

        conn = get_db()
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?,?)",
            (user, pwd)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -------- BOOKING --------
@app.route('/book/<movie>', methods=["GET", "POST"])
def book(movie):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    rows = conn.execute(
        "SELECT seats FROM bookings WHERE movie=?",
        (movie,)
    ).fetchall()

    booked_seats = []
    for r in rows:
        if r["seats"]:
            booked_seats += r["seats"].split(",")

    if request.method == "POST":
        seats = request.form.get('seats')
        user = session["user"]

        conn.execute(
            "INSERT INTO bookings (username, movie, seats) VALUES (?,?,?)",
            (user, movie, seats)
        )
        conn.commit()
        conn.close()

        return render_template("success.html", movie=movie, seats=seats)

    conn.close()

    return render_template(
        "book.html",
        movie=movie,
        booked_seats=booked_seats
    )

# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)