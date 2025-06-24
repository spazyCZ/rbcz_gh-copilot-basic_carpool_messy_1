# BAD: No imports organization, mixing standard lib with third-party
from flask import Flask, render_template_string, request, redirect, url_for, session
import json
import os
from datetime import datetime

# BAD: Global variables everywhere
app = Flask(__name__)
app.secret_key = "123"  # BAD: Hardcoded weak secret key

# BAD: Global data storage, poor variable names
data = {}
spots = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2"]
users = {"admin": "admin", "user": "pass"}  # BAD: Hardcoded credentials in plain text
file_path = "data.json"  # BAD: Changed to JSON but still bad practices

# BAD: More global variables for poor JSON handling
backup_file = "backup.json"
log_file = "actions.json"
user_file = "users.json"

# BAD: HTML mixed with Python code, no templates
html1 = """
<!DOCTYPE html>
<html>
<head><title>Parking System</title></head>
<body bgcolor="lightblue">
<h1 style="color:red;">PARKING RESERVATION SYSTEM</h1>
{% if not session.get('user') %}
<form method="post" action="/login">
Username: <input name="u" type="text"><br><br>
Password: <input name="p" type="password"><br><br>
<input type="submit" value="LOGIN">
</form>
{% else %}
<p>Welcome {{ session['user'] }}! <a href="/logout">Logout</a></p>
<h2>Available Spots:</h2>
<ul>
{% for s in spots %}
<li>{{ s }} 
{% if s in data %}
- RESERVED by {{ data[s]['n'] }} on {{ data[s]['d'] }}
<a href="/del?spot={{ s }}">DELETE</a>
{% else %}
- FREE <a href="/book?spot={{ s }}">BOOK NOW</a>
{% endif %}
</li>
{% endfor %}
</ul>
<h3>Add New Reservation:</h3>
<form method="post" action="/add">
Spot: <select name="spot">
{% for s in spots %}
<option value="{{ s }}">{{ s }}</option>
{% endfor %}
</select><br>
Name: <input name="name"><br>
Date: <input name="date" type="date"><br>
<input type="submit" value="RESERVE">
</form>
{% endif %}
</body>
</html>
"""

# BAD: Function doing too many things, no error handling
def load_data():
    global data
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
    except:
        data = {}

def save_data():
    global data
    try:
        with open(file_path, "w") as f:
            json.dump(data, f)
    except:
        pass

# BAD: Redundant data loading function
def load_backup():
    try:
        with open(backup_file, "r") as f:
            return json.load(f)
    except:
        return {}

# BAD: Writing to multiple JSON files unnecessarily
def save_backup():
    try:
        with open(backup_file, "w") as f:
            json.dump(data, f, indent=4)  # BAD: Inconsistent formatting
        with open(log_file, "a") as f:
            json.dump({"action": "backup", "time": str(datetime.now())}, f)
            f.write("\n")  # BAD: Malformed JSON file
    except:
        pass

# BAD: No route organization, mixing logic in routes
@app.route("/")
def home():
    load_data()  # BAD: Loading data on every request
    return render_template_string(html1, spots=spots, data=data, session=session)

@app.route("/login", methods=["POST"])
def login():
    u = request.form["u"]
    p = request.form["p"]
    # BAD: No input validation, vulnerable to timing attacks
    if u in users and users[u] == p:
        session["user"] = u
    return redirect("/")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/add", methods=["POST"])
def add():
    # BAD: No authentication check, no validation
    spot = request.form["spot"]
    name = request.form["name"]
    date = request.form["date"]
    
    load_data()
    load_backup()  # BAD: Loading backup data but not using it
    # BAD: No double-booking prevention
    data[spot] = {"n": name, "d": date}
    save_data()
    save_backup()  # BAD: Unnecessary backup on every operation
    return redirect("/")

@app.route("/book")
def book():
    spot = request.args.get("spot")
    load_data()
    # BAD: No validation, direct assignment
    data[spot] = {"n": "Quick Booking", "d": str(datetime.now().date())}
    save_data()
    return redirect("/")

@app.route("/del")
def delete():
    spot = request.args.get("spot")
    load_data()
    # BAD: No error handling if key doesn't exist
    try:
        del data[spot]
    except:
        pass
    save_data()
    return redirect("/")

# BAD: Admin route with no proper authentication
@app.route("/admin")
def admin():
    load_data()
    # BAD: Exposing internal data structure
    return f"<pre>{data}</pre><br><a href='/'>Back</a>"

# BAD: Debug route in production code
@app.route("/debug")
def debug():
    return f"<h1>Debug Info</h1><p>Users: {users}</p><p>Data: {data}</p><p>Session: {session}</p>"

# BAD: Catch-all error handler that exposes too much
@app.errorhandler(404)
def not_found(error):
    return f"<h1>404 Error</h1><p>Path not found: {request.path}</p><p>Method: {request.method}</p>"

# BAD: Running with debug=True, no port configuration
if __name__ == "__main__":
    load_data()
    app.run(debug=True, host="0.0.0.0")  # BAD: Binding to all interfaces in debug mode
