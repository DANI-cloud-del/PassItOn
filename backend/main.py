from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)  # For session management

@app.route('/')
def home():
    user = session.get('username', 'Guest')
    return render_template('home.html', user=user)

app.run(debug=True)