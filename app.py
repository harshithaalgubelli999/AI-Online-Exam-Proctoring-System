from flask import Flask, render_template, request, redirect, url_for
import database

app = Flask(__name__)

# Initialize database
database.init_db()

# ------------------ LOGIN ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("login.html")

# ------------------ DASHBOARD ------------------
@app.route("/dashboard")
def dashboard():
    results = database.get_results()
    return render_template("dashboard.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
