from flask import Flask, redirect, render_template, request, session, flash
from pull_data import kp_search
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import datetime
from statistics import mean, median

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

# Define warning message when required field is not filled
generic_warning_message = "Please fill out this field."

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        # Ensure user provides search word and selects website
        if not request.form.get("keyword"):
            return render_template("home.html", warning = generic_warning_message, search_error = True)
        elif not request.form.get("selected_website"):
            return render_template("home.html", warning = "Please select website.", select_error = True)

        keyword = request.form.get("keyword")

        # Utilizes function for searching items from kp (short for kupujemprodajem) website
        items, count = kp_search(keyword)
        print(count)
        
        if not items:
            # Inform user that search does not produce results
            flash(f"There are {count} results for '{keyword}'.")
            return render_template("home.html")

        # Record search history and add items to SQL database if user is logged in
        if "user" in session:
            time = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
            db.execute("INSERT INTO history (user_id, search_keyword, time) VALUES (?, ?, ?)", (session["id"], keyword, time))
            con.commit()
            # Get search_id
            search_history = db.execute("SELECT id FROM history WHERE user_id = ? AND time = ?", (session["id"], time))
            search_id = search_history.fetchone()[0]

            for item in items:
                db.execute("INSERT INTO search (search_id, item, price) VALUES (?, ?, ?)", (search_id, item.name, item.price))
                con.commit()

        # Shows mean and median price to the user
        prices = [item.price for item in items]
        mean_price, median_price = round(mean(prices), 2), median(prices)

        flash(f"Search successful!\nThere are {count} results for '{keyword}', mean and median prices are {mean_price} € and {median_price} €, respectively.")
        return render_template("home.html") #+ \
            #'<script>document.getElementById("loading_header").style.display = "none"; document.getElementById("loading_bar").style.display = "none";</script>'
    else:
        return render_template("home.html")

@app.route("/search_history", methods=["GET"])
def search_history():

    if "user" in session:
        id = session["id"]

        rows = db.execute("SELECT id, search_keyword, time FROM history WHERE user_id = ?", (id, ))
        history = rows.fetchall()

        # Notifies user in case where they did not conduct any search
        if history == None:
            flash("Search history results are unavailable, you need to conduct a search first.")
            return render_template("search_history.html")

        results = []
        for search_id, search_keyword, time in history:

            rows = db.execute("SELECT COUNT(item), AVG(price) FROM search WHERE search_id = ?", (search_id, ))
            count_and_mean = rows.fetchone()
            count, mean = count_and_mean[0], count_and_mean[1]

            rows = db.execute("SELECT price FROM search WHERE search_id = ?", (search_id, ))
            prices = rows.fetchall()
            prices = [price[0] for price in prices]
            med = median(prices)

            print(search_keyword, time, count, round(mean, 2), med)

            results.append([search_keyword, time, count, round(mean, 2), med])

        return render_template("search_history.html", results = results)

    flash("You must be logged in to access search history.")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        # Ensure user provides username
        if not request.form.get("username"):
            return render_template("register.html", warning = generic_warning_message, username_error = True)

        row = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"), ))
        check_username = row.fetchone()

        # Ensure username does not already exists and that passwords match
        if check_username:
            return render_template("register.html", warning = f'Username "{check_username[1]}" is taken.', username_error = True)
        elif not request.form.get("password"):
            return render_template("register.html", warning = generic_warning_message, password_error = True)
        elif not request.form.get("confirmation"):
            return render_template("register.html", warning = generic_warning_message, confirmation_error = True)
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("register.html", warning = "Password do not match.", confirmation_error = True)
        
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Ensure password contains 6 characters including at least one uppercase character one lowercase character and one number
        numerical_characters = [str(x) for x in range(10)]
        if len(password) < 6:
            return render_template("register.html", warning = "Password must contain 6 characters.", password_error = True)
        elif not any(letter.isupper() for letter in password):
            return render_template("register.html", warning = "Password does not contain uppercase character.", password_error = True)
        elif not any(letter.islower() for letter in password):
            return render_template("register.html", warning = "Password does not contain lowercase character.", password_error = True)
        elif not any(number in password for number in numerical_characters):
            return render_template("register.html", warning = "Password does not contain number.", password_error = True)

        # Hash user password and add username and password to the sql database
        hash_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash_password) VALUES (?, ?)", (username, hash_password))
        con.commit()

        flash("Registration successful, please proceed to log in.")
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user" in session:
        flash("You are already logged in!")
        return render_template("login.html")

    if request.method == "POST":
        # Ensure user provides username and password
        if not request.form.get("username"):
            return render_template("login.html", warning = generic_warning_message, username_error = True)
        elif not request.form.get("password"):
            return render_template("login.html", warning = generic_warning_message, password_error = True)

        row = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"), ))
        check_username_password = row.fetchone()

        # If logged user try to log in again return him to home page
        if "user" in session and session["user"] == check_username_password[1]:
            flash("You are already logged in!")
            return redirect("/")

        # Check if username exists and password is correct
        if not check_username_password:
            return render_template("login.html", warning = "Username does not exist.", username_error = True)
        elif not check_password_hash(check_username_password[-1], request.form.get("password")):
            return render_template("login.html", warning = "Wrong password.", password_error = True)

        # Clear session if previous user was loged in and start new session 
        session.clear()
        session["id"] = check_username_password[0]
        session["user"] = check_username_password[1]
        
        flash(f"Hi {check_username_password[1]}, you have been logged in.")
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout",  methods=["GET"])
def logout():

    # Check if user is loged in
    if "user" in session:
        user = session["user"]
        session.clear()
        flash(f"{user} have been logged out.")
        return redirect("/")

    # If the user is not loged in, redirect to current page
    flash("You are not logged in.")
    return redirect(request.referrer)

@app.route("/about",  methods=["GET"])
def about():
    # If the user is not loged in, redirect to current page
    flash("To be added.")
    return render_template("about.html")