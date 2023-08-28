from flask import Flask, render_template
from app import app

app = Flask(__name__)
app.secret_key = 'huonwe'

@app.route("/index",methods=["GET"])
def index():
    return render_template("HTML/index.html")