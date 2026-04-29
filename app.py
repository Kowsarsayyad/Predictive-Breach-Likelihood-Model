from flask import Flask, render_template, request, redirect, session
import joblib
import json
import os
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# Load ML model
model = joblib.load("model.pkl")

USERS_FILE = "users.json"


# ===============================
# SAFE LOAD USERS FUNCTION
# ===============================
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ===============================
# HOME
# ===============================
@app.route("/")
def home():
    return redirect("/login")


# ===============================
# REGISTER
# ===============================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        users = load_users()

        username = request.form["username"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()

        if password != confirm_password:
            return "❌ Passwords do not match!"

        if username in users:
            return "⚠ User already exists!"

        # Hash password before saving
        hashed_password = generate_password_hash(password)

        users[username] = hashed_password
        save_users(users)

        return redirect("/login")

    return render_template("register.html")


# ===============================
# LOGIN
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        users = load_users()

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if username in users and check_password_hash(users[username], password):
            session["user"] = username
            return redirect("/dashboard")

        return "❌ Invalid Credentials"

    return render_template("login.html")


# ===============================
# DASHBOARD
# ===============================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect("/login")

    prediction = None
    risk_percent = None
    advice = None

    if request.method == "POST":
        try:
            failed_logins = int(request.form["failed_logins"])
            open_ports = int(request.form["open_ports"])
            outdated_patches = int(request.form["outdated_patches"])
            traffic_spike = int(request.form["traffic_spike"])
            phishing_reports = int(request.form["phishing_reports"])

            inputs = np.array([[failed_logins, open_ports,
                                outdated_patches, traffic_spike,
                                phishing_reports]])

            pred = model.predict(inputs)[0]
            prob = model.predict_proba(inputs)[0][1]

            risk_percent = round(prob * 100, 2)

            if pred == 1:
                prediction = "🚨 High Breach Risk"
                advice = """
                Immediate Actions Required:
                • Apply security patches
                • Close unused ports
                • Enable Multi-Factor Authentication
                • Investigate abnormal traffic
                """
            else:
                prediction = "✅ Low Breach Risk"
                advice = """
                System appears secure.
                • Continue monitoring
                • Perform regular audits
                • Maintain patch updates
                """

        except Exception as e:
            prediction = "Error in input values"
            advice = str(e)

    return render_template("dashboard.html",
                           user=session["user"],
                           prediction=prediction,
                           risk=risk_percent,
                           advice=advice)


# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    app.run(debug=True)