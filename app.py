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

# --- IMPORTANT ---
# Removed the subprocess.run(["yt-dlp", "-U"]) call at app startup.
# On Render, rely on your requirements.txt for yt-dlp version and trigger
# a "Clear cache & deploy" to ensure it's updated during the build process.
# Running it at runtime adds delay and can cause issues.

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# List of rotating user-agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
]

# Proxy pool - replace with YOUR OWN if possible, free ones are highly unreliable
DEFAULT_PROXIES = [
    "http://20.206.106.192:80", # Example - probably dead
    "http://47.74.152.29:8888", # Example - probably dead
    "http://190.2.137.49:80", # Example - probably dead
    # Add your own reliable proxies here
]
PROXIES = os.environ.get("PROXY_LIST", ",".join(DEFAULT_PROXIES)).split(",")
PROXIES = [p.strip() for p in PROXIES if p.strip()]

if not PROXIES:
    logging.warning("No proxies set from environment. Using default (likely dead) proxies or none. This might still trigger bot detection on heavy use.")
else:
    logging.info(f"Loaded {len(PROXIES)} proxies from PROXY_LIST environment variable.")


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

        # Basic URL validation for YouTube
        if not re.match(YOUTUBE_REGEX, url):
            message = "❌ That's not a valid YouTube URL. Please provide a direct YouTube video link."
            return render_template("index.html", message=message)

        downloaded_filepath = None
        try:
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            downloaded_filepath = filepath # Store for cleanup

            logging.info(f"Attempting to download: {url} to {filepath}")

            user_agent = random.choice(USER_AGENTS)
            proxy = random.choice(PROXIES) if PROXIES else None

            # Base yt-dlp command
            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", filepath,
                "--no-warnings", # Suppress non-critical warnings
                "--user-agent", user_agent,
                "--retries", "10",
                "--retry-sleep", "exp=1:60", # Exponential backoff for retries
                "--fragment-retries", "10",
                "--force-ipv4", # Avoid IPv6 detection issues
                "--geo-bypass", # Try to bypass geo-restrictions
                "--max-filesize", "150M" # Adjusted for Render's 512MB RAM
            ]

            if proxy:
                cmd.extend(["--proxy", proxy])
                logging.info(f"Using proxy: {proxy} and User-Agent: {user_agent}")
            else:
                logging.info(f"No proxy used. User-Agent: {user_agent}")

            # Add a small random sleep to mimic human behavior before first attempt
            time.sleep(random.uniform(1, 3))

            logging.info(f"Executing yt-dlp command (attempt 1): {' '.join(cmd + [url])}")
            result = subprocess.run(cmd + [url], capture_output=True, text=True, timeout=600) # Timeout after 10 min

            # Check if first attempt failed
            if result.returncode != 0 or not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                logging.error(f"First yt-dlp attempt failed (return code {result.returncode}).")
                logging.error(f"STDOUT: {result.stdout}")
                logging.error(f"STDERR: {result.stderr}")
                logging.info("Retrying with a different proxy/User-Agent...")

                # --- Prepare for Retry Attempt ---
                user_agent_retry = random.choice(USER_AGENTS)
                proxy_retry = random.choice(PROXIES) if PROXIES else None

                # Rebuild cmd for retry to ensure clean proxy/UA update
                cmd_retry = [
                    "yt-dlp",
                    "-f", "best[ext=mp4]/best",
                    "-o", filepath,
                    "--no-warnings",
                    "--user-agent", user_agent_retry,
                    "--retries", "10",
                    "--retry-sleep", "exp=1:60",
                    "--fragment-retries", "10",
                    "--force-ipv4",
                    "--geo-bypass",
                    "--max-filesize", "150M"
                ]
                if proxy_retry:
                    cmd_retry.extend(["--proxy", proxy_retry])
                    logging.info(f"Using retry proxy: {proxy_retry} and User-Agent: {user_agent_retry}")
                else:
                    logging.info(f"No retry proxy used. User-Agent: {user_agent_retry}")

                # Add a slightly longer random sleep before retry
                time.sleep(random.uniform(2, 5))

                logging.info(f"Executing yt-dlp command (attempt 2): {' '.join(cmd_retry + [url])}")
                result = subprocess.run(cmd_retry + [url], capture_output=True, text=True, timeout=600)

                # Check if second attempt also failed
                if result.returncode != 0:
                    logging.error(f"Second yt-dlp attempt failed (return code {result.returncode}).")
                    logging.error(f"STDOUT: {result.stdout}")
                    logging.error(f"STDERR: {result.stderr}")
                    # Re-raise the exception to be caught by the outer try-except block
                    raise Exception(f"Download failed even after retry. Error: {result.stderr.strip()}")
                elif not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                    logging.error(f"Second yt-dlp attempt succeeded, but file is missing or empty. STDOUT: {result.stdout}")
                    raise Exception("Download completed but the file is empty or missing on disk.")


            # --- Cleanup function for the temporary downloaded file ---
            @after_this_request
            def cleanup(response):
                try:
                    if downloaded_filepath and os.path.exists(downloaded_filepath):
                        os.remove(downloaded_filepath)
                        logging.info(f"Deleted temporary file: {downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Cleanup failed for {downloaded_filepath}: {e}")
                return response

            # --- Send the file to the user ---
            return send_file(filepath, as_attachment=True, download_name="video.mp4", mimetype="video/mp4")

        # --- Specific Exception Handling ---
        except subprocess.TimeoutExpired as e:
            logging.error(f"yt-dlp process timed out after {e.timeout} seconds for URL: {url}", exc_info=True)
            if e.stdout: logging.error(f"Timeout STDOUT: {e.stdout}")
            if e.stderr: logging.error(f"Timeout STDERR: {e.stderr}")
            message = "❌ Error: The download timed out (over 10 minutes). The video might be too large or the connection too slow. Try a shorter video."
        except Exception as e:
            logging.error(f"An unexpected error occurred during the download process for URL: {url}", exc_info=True)
            # General error message from the raised Exception (e.g., from yt-dlp's stderr)
            message = f"❌ Error: {str(e)}. This could be a YouTube issue, an invalid URL, or a proxy problem. Try a different video."

    return render_template("index.html", message=message)

if __name__ == "__main__":
    # When running locally, Flask debug mode is useful.
    # On Render, Gunicorn typically manages the app and provides logging.
    # Ensure your Render 'start command' uses Gunicorn and binds to $PORT.
    # Example Render Start Command: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1
    app.run(debug=True, host="0.0.0.0", port=5000)
