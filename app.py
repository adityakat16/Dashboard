from flask import Flask, request, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

@app.route("/", methods=["GET", "POST"])
def index():
    msg = ""
    if request.method == "POST":
        symbol = request.form["symbol"].upper()
        # Google Sheets Auth (keep your JSON file secure, use env vars in prod)
        creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open("StockRequestSystem").worksheet("Requests")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([symbol, "pending", now])
        msg = f"✅ Request for {symbol} submitted!"
    return render_template("index.html", message=msg)
