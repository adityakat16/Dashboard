import os
import uuid
import subprocess
import logging
from flask import Flask, render_template, request, send_file, after_this_request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Attempt to auto-update yt-dlp (optional but useful)
try:
    subprocess.run(["yt-dlp", "-U"], check=True)
    logging.info("yt-dlp updated successfully.")
except Exception as e:
    logging.warning(f"Failed to update yt-dlp: {e}. Proceeding with installed version.")

app = Flask(__name__)

# Directory to store downloaded videos
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Load cookies from environment variable (if any)
COOKIES_CONTENT = os.environ.get("YOUTUBE_COOKIES_CONTENT")
COOKIES_FILE_NAME = "youtube_cookies.txt"

if COOKIES_CONTENT:
    try:
        with open(COOKIES_FILE_NAME, "w") as f:
            f.write(COOKIES_CONTENT)
        logging.info(f"Cookies file created: {COOKIES_FILE_NAME}")
    except Exception as e:
        logging.error(f"Error creating cookies file: {e}")
        COOKIES_CONTENT = None
else:
    logging.warning("No cookies configured. You may encounter YouTube download limits or 429 errors.")

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()

        if not url:
            message = "❌ Please enter a valid YouTube URL."
            return render_template("index.html", message=message)

        if "youtube.com/" not in url and "youtu.be/" not in url:
            message = "❌ Please enter a valid YouTube video URL (youtube.com or youtu.be)."
            return render_template("index.html", message=message)

        downloaded_filepath = None

        try:
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            downloaded_filepath = filepath

            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", filepath,
                "--no-warnings",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "--retries", "5",
                "--retry-sleep", "5:10",
                "--max-filesize", "500M"
            ]

            # Optional: Proxy usage
            proxy_url = os.environ.get("PROXY_URL")
            if proxy_url:
                cmd.extend(["--proxy", proxy_url])
                logging.info(f"Using proxy: {proxy_url}")

            # Optional: Add cookies file
            if COOKIES_CONTENT and os.path.exists(COOKIES_FILE_NAME):
                cmd.extend(["--cookies", COOKIES_FILE_NAME])
                logging.info(f"Using cookies file: {COOKIES_FILE_NAME}")

            cmd.append(url)

            process_timeout = 600  # 10 minutes max
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=process_timeout
            )

            if result.stdout:
                logging.info(f"yt-dlp output:\n{result.stdout}")
            if result.stderr:
                logging.error(f"yt-dlp error:\n{result.stderr}")

            if result.returncode != 0:
                raise Exception(result.stderr.strip() or "Unknown error occurred.")

            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                raise Exception("Download failed: File not created or is empty.")

            logging.info(f"Download complete: {filepath}")

            @after_this_request
            def remove_file(response):
                try:
                    if downloaded_filepath and os.path.exists(downloaded_filepath):
                        os.remove(downloaded_filepath)
                        logging.info(f"Cleaned up file: {downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Error during file cleanup: {e}")
                return response

            return send_file(
                filepath,
                as_attachment=True,
                download_name="youtube_video.mp4",
                mimetype="video/mp4"
            )

        except FileNotFoundError:
            message = "❌ Error: yt-dlp not found. Please install yt-dlp."
            logging.error(message)
        except subprocess.TimeoutExpired:
            message = f"❌ Error: Download timed out after {process_timeout} seconds."
            logging.error(message)
        except Exception as e:
            message = f"❌ An error occurred: {str(e)}"
            logging.error(f"Unhandled error: {e}")
        finally:
            if downloaded_filepath and os.path.exists(downloaded_filepath):
                try:
                    os.remove(downloaded_filepath)
                    logging.info(f"Cleaned up file (on error): {downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Error cleaning up file: {e}")

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
