from flask import Flask, redirect, render_template, request, session
from pull_data import kp_search
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = generate_password_hash("Not very secret key")

con = sqlite3.connect('SAH.db', check_same_thread=False)
db = con.cursor()

""" @app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response """

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        # Works just for kupujemprodajem for now
        website = request.form.get("selected_website")
        if not keyword:
            # TODO: Add invalid input notification
            return render_template("home.html")

        items, count = kp_search(keyword)
        #TODO: Add items to SQL database

        print(keyword, website, count)
        return render_template("home.html")
    else:
        return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        generic_warning = "Please fill out this field."
        if not request.form.get("username"):
            return render_template("register.html", warning = generic_warning, username_error = True)

        row = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        check_username = row.fetchone()

        if check_username:
            return render_template("register.html", warning = f'Username "{check_username[1]}" is taken.', username_error = True)
        elif not request.form.get("password"):
            return render_template("register.html", warning = generic_warning, password_error = True)
        elif not request.form.get("confirmation"):
            return render_template("register.html", warning = generic_warning, confirmation_error = True)
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("register.html", warning = "Password do not match.", confirmation_error = True)
        
        username = request.form.get("username")
        password = request.form.get("password")

        numerical_characters = [str(x) for x in range(10)]
        if len(password) < 6:
            return render_template("register.html", warning = "Password must contain 6 characters.", password_error = True)
        elif not any(letter.isupper() for letter in password):
            return render_template("register.html", warning = "Password does not contain uppercase character.", password_error = True)
        elif not any(letter.islower() for letter in password):
            return render_template("register.html", warning = "Password does not contain lowercase character.", password_error = True)
        elif not any(number in password for number in numerical_characters):
            return render_template("register.html", warning = "Password does not contain number", password_error = True)

        hash_password = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash_password) VALUES (?, ?)", (username, hash_password))
        con.commit()

        session["user"] = username

        return render_template("home.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        return render_template("login.html")

    return render_template("login.html")

@app.route("/logout",  methods=["GET"])
def logout():
    if "user" in session:
        session.clear()
        return redirect("/")
    return redirect(request.referrer)