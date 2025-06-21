from flask import Flask, request, render_template
from sele import run_scraper
import os
import traceback

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        stock = request.form.get("stock")
        if stock:
            try:
                data = run_scraper(stock)
                return render_template("results.html", data=data)
            except Exception as e:
                traceback.print_exc()  # ✅ full error will show in logs
                return f"<h3>❌ Error during scraping: {e}</h3>"
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
