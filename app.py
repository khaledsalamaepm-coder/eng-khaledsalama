import json, os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret123"

DATA_FILE = "messages.json"
USERS_FILE = "users.json"
UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

messages = load(DATA_FILE)
users = load(USERS_FILE)

html = """
<!DOCTYPE html>
<html>
<head>
<title>eng.khaledsalama</title>
<style>
body {font-family:Arial; background:#f5f5f5;}
main {max-width:800px; margin:auto; background:white; padding:20px;}
img {max-width:200px;}
.message {border-bottom:1px solid #ddd; padding:10px;}
</style>
</head>
<body>

<main>

<h1>eng.khaledsalama</h1>

{% if session.user %}
<p>Welcome {{session.user}} | <a href="/logout">Logout</a></p>

<form action="/submit" method="POST" enctype="multipart/form-data">
<input name="message" placeholder="Write message" required>
<input type="file" name="image">
<button>Send</button>
</form>

{% else %}
<a href="/login">Login</a> | <a href="/register">Register</a>
{% endif %}

<hr>

{% for m in messages %}
<div class="message">
<strong>{{m.user}}</strong>: {{m.text}} <br>
<small>{{m.time}}</small><br>

{% if m.image %}
<img src="{{m.image}}">
{% endif %}

</div>
{% endfor %}

</main>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html, messages=messages)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        users.append({
            "user": request.form['user'],
            "pass": request.form['pass']
        })
        save(USERS_FILE, users)
        return redirect('/login')
    return """
    <form method="POST">
    <input name="user" placeholder="Username">
    <input name="pass" type="password" placeholder="Password">
    <button>Register</button>
    </form>
    """

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        for u in users:
            if u["user"] == request.form['user'] and u["pass"] == request.form['pass']:
                session['user'] = u["user"]
                return redirect('/')
    return """
    <form method="POST">
    <input name="user">
    <input name="pass" type="password">
    <button>Login</button>
    </form>
    """

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/submit', methods=['POST'])
def submit():
    if 'user' not in session:
        return redirect('/login')

    file = request.files.get('image')
    image_path = ""

    if file and file.filename:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        image_path = path

    messages.append({
        "user": session['user'],
        "text": request.form['message'],
        "image": image_path,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    save(DATA_FILE, messages)
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)