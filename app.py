from flask import Flask, request, render_template
from sele import run_scraper

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    error = None
    if request.method == "POST":
        stock = request.form.get("stock")
        try:
            data = run_scraper(stock)
        except Exception as e:
            error = f"❌ Error during scraping: {e}"
    return render_template("index.html", data=data, error=error)
