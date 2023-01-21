from flask import Flask, redirect, render_template, request, session
from pull_data import kp_search


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

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
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")
