from flask import Flask, request, render_template
from sele import run_scraper  # import your scraper

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    if request.method == "POST":
        stock = request.form["stock"]
        data = run_scraper(stock)
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
