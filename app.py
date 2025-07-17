import os
import uuid
import subprocess
import logging
import random
import time
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

{e}")

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# List of rotating user-agents (add more if you want, you lazy fuck)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
]

# Proxy pool (add your own, or use free ones – but free ones suck balls and die quick)
# Set via env var: PROXY_LIST="http://proxy1:port,http://proxy2:port"
DEFAULT_PROXIES = [
    # Example free proxies (replace with real ones, these are placeholders and probably dead)
    "http://20.206.106.192:80",
    "http://47.74.152.29:8888",
    "http://190.2.137.49:80",
    "http://207.166.178.240",
    "http://123.141.181.8",
    "http://159.203.61.169",
    "http://167.99.124.118",
    "http://219.65.73.81",
    "http://139.59.1.14",
    "http://38.147.98.190"
]
PROXIES = os.environ.get("PROXY_LIST", ",".join(DEFAULT_PROXIES)).split(",")
PROXIES = [p.strip() for p in PROXIES if p.strip()]

if not PROXIES:
    logging.warning("No proxies set. This might still trigger bot detection on heavy use.")

# Accept various YouTube formats
YOUTUBE_REGEX = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()

        if not url:
            message = "❌ Please enter a YouTube video URL."
            return render_template("index.html", message=message)

        if not re.match(YOUTUBE_REGEX, url):
            message = "❌ That's not a valid YouTube URL."
            return render_template("index.html", message=message)

        downloaded_filepath = None
        try:
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            downloaded_filepath = filepath

            logging.info(f"Downloading: {url}{url} → {filepath}")

            # Pick a random user-agent
            user_agent = random.choice(USER_AGENTS)

            # Pick a random proxy if available
            proxy = random.choice(PROXIES) if PROXIES else None

            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", filepath,
                "--no-warnings",
                "--user-agent", user_agent,
                "--retries", "10",  # More retries for robustness
                "--retry-sleep", "exp=1:60",  # Exponential backoff sleep (1s to 60s)
                "--fragment-retries", "10",
                "--force-ipv4",  # Avoid IPv6 detection issues
                "--geo-bypass",  # Try to bypass geo-restrictions
                "--max-filesize", "500M"
            ]

            if proxy:
                cmd += ["--proxy", proxy]
                logging.info(f"Using proxy: {proxy} and User-Agent: {user_agent}")

            # Add a small random sleep to mimic human behavior
            time.sleep(random.uniform(1, 3))

            result = subprocess.run(cmd + [url], capture_output=True, text=True, timeout=600)

            if result.returncode != 0 or not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                logging.error(result.stderr)
                # If it fails, try once more with a different proxy/UA
                logging.info("First attempt failed, retrying with new proxy/UA...")
                user_agent = random.choice(USER_AGENTS)
                proxy = random.choice(PROXIES) if PROXIES else None
                if proxy:
                    cmd += ["--proxy", proxy]  # Update proxy in cmd
                cmd[cmd.index("--user-agent") + 1] = user_agent  # Update UA
                time.sleep(random.uniform(2, 5))
                result = subprocess.run(cmd + [url], capture_output=True, text=True, timeout=600)
                if result.returncode != 0:
                    raise Exception(f"Download failed even after retry. Error: {result.stderr}")

            @after_this_request
            def cleanup(response):
                try:
                    if os.path.exists(downloaded_filepath):
                        os.remove(downloaded_filepath)
                        logging.info(f"Deleted: {downloaded_filepath}")
{downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Cleanup failed: {e}")
{e}")
                return response

            return send_file(filepath, as_attachment=True, download_name="video.mp4", mimetype="video/mp4")

        except Exception as e:
            logging.error(f"Exception: {e}")
{e}")
            message = f"❌ Error: {str(e)}. Try a different URL or check your proxies, shithead."

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
