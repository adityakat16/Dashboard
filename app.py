from flask import Flask, request, render_template
from sele import run_scraper  # import your scraper
import os


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    if request.method == "POST":
        stock = request.form["stock"]
        data = run_scraper(stock)
    return render_template("index.html", data=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
