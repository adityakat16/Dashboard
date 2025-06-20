from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/getdata", methods=["POST"])
def getdata():
    stock = request.form["stock"]
    
    # run your selenium script (pass stock if needed)
    subprocess.run(["python", "sele.py", stock])

    # fetch results (e.g., from CSV or SQLite)
    with open("output.csv", "r") as f:
        data = f.read()

    return f"<h1>Data for {stock}</h1><pre>{data}</pre>"
