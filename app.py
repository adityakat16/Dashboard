import os
import uuid
import subprocess
import logging
from flask import Flask, render_template, request, send_file, after_this_request
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Try to auto-update yt-dlp
try:
    subprocess.run(["yt-dlp", "-U"], check=True)
    logging.info("yt-dlp updated successfully.")
except Exception as e:
    logging.warning(f"Failed to update yt-dlp: {e}")

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Load cookies if available
COOKIES_CONTENT = os.environ.get("YOUTUBE_COOKIES_CONTENT")
COOKIES_FILE_NAME = "youtube_cookies.txt"

if COOKIES_CONTENT:
    try:
        with open(COOKIES_FILE_NAME, "w") as f:
            f.write(COOKIES_CONTENT)
        logging.info(f"Cookies file created: {COOKIES_FILE_NAME}")
    except Exception as e:
        logging.error(f"Failed to create cookies file: {e}")
        COOKIES_CONTENT = None
else:
    logging.warning("No YOUTUBE_COOKIES_CONTENT set. You may encounter 429 errors.")

# Accept various YouTube formats
YOUTUBE_REGEX = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        # Get from form input named "symbol"
        url = request.form.get("url", "").strip()

        if not url:
            message = "❌ Please enter a YouTube video URL."
            return render_template("index.html", message=message)

        if not re.match(YOUTUBE_REGEX, url):
            message = "❌ Please enter a valid YouTube URL."
            return render_template("index.html", message=message)

        downloaded_filepath = None
        try:
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            downloaded_filepath = filepath

            logging.info(f"Downloading: {url} → {filepath}")

            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", filepath,
                "--no-warnings",
                "--user-agent", "Mozilla/5.0",
                "--retries", "5",
                "--retry-sleep", "3:6",
                "--max-filesize", "500M"
            ]

            proxy_url = os.environ.get("PROXY_URL")
            if proxy_url:
                cmd += ["--proxy", proxy_url]
                logging.info(f"Using proxy: {proxy_url}")

            if COOKIES_CONTENT and os.path.exists(COOKIES_FILE_NAME):
                cmd += ["--cookies", COOKIES_FILE_NAME]
                logging.info(f"Using cookies: {COOKIES_FILE_NAME}")

            result = subprocess.run(cmd + [url], capture_output=True, text=True, timeout=600)

            if result.returncode != 0 or not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                logging.error(result.stderr)
                raise Exception("Download failed. Check logs for details.")

            @after_this_request
            def cleanup(response):
                try:
                    if os.path.exists(downloaded_filepath):
                        os.remove(downloaded_filepath)
                        logging.info(f"Deleted: {downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Cleanup failed: {e}")
                return response

            return send_file(filepath, as_attachment=True, download_name="video.mp4", mimetype="video/mp4")

        except Exception as e:
            logging.error(f"Exception: {e}")
            message = f"❌ Error: {str(e)}"

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
